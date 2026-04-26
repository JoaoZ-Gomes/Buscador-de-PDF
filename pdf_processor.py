import os
import glob
import logging
import fitz  # PyMuPDF
from concurrent.futures import ProcessPoolExecutor, as_completed
import threading
from utils import normalize_text, reserve_unique_filepath, _filename_lock

logger = logging.getLogger(__name__)

# Variável global no processo worker para armazenar o lock compartilhado
_worker_lock = None

def _worker_initializer(lock):
    """Recebe o lock compartilhado e o armazena no escopo global do worker."""
    global _worker_lock
    _worker_lock = lock

def _process_pdf_worker(pdf_path, filename, search_name, search_name_normalized, target_dir):
    matches_found = 0
    doc = None
    try:
        doc = fitz.open(pdf_path)
        
        if doc.needs_pass:
            logger.warning(f"Ignorando PDF protegido por senha: {pdf_path}")
            return matches_found
            
        found_pages = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text:
                normalized_text = normalize_text(text)
                if search_name_normalized in normalized_text:
                    found_pages.append(page_num)
                    
        base_name = os.path.splitext(filename)[0]
        safe_search_name = "".join(x for x in search_name if x.isalnum() or x in " _-")
        safe_search_name = safe_search_name.strip().replace(" ", "_")

        for page_num in found_pages:
            new_doc = fitz.open()
            output_path = None
            try:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                new_filename = f"{base_name}_pagina{page_num + 1}_{safe_search_name}.pdf"
                
                # Reserva atomicamente o nome do arquivo usando o lock compartilhado
                # para evitar race conditions quando múltiplos processos gravam simultaneamente
                output_path = reserve_unique_filepath(target_dir, new_filename, _worker_lock)
                
                new_doc.save(output_path)
                matches_found += 1
            except Exception as e:
                logger.error(f"Erro ao salvar página {page_num + 1} de {pdf_path}: {e}")
                # Remove o arquivo placeholder vazio se o save falhou
                if output_path and os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
            finally:
                new_doc.close()
            
        return matches_found
            
    except Exception as e:
        logger.error(f"Erro ao ler o PDF {pdf_path}: {e}")
        return 0
    finally:
        # Garante que o documento fonte é sempre fechado, mesmo em caso de exceção
        if doc is not None:
            doc.close()

class PDFSearcher:
    def __init__(self, source_dir, target_dir, search_name, update_callback, completion_callback):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.search_name = search_name
        self.search_name_normalized = normalize_text(search_name)
        self.update_callback = update_callback
        self.completion_callback = completion_callback
        self.is_running = False
        self.total_pdfs = 0
        self.processed_pdfs = 0
        self.total_matches = 0
        self.lock = threading.Lock()
        self._executor = None  # Referência ao pool de processos para shutdown forçado

    def get_all_pdfs(self):
        search_path = os.path.join(self.source_dir, "**", "*.pdf")
        return glob.glob(search_path, recursive=True)
        
    def start_search(self):
        self.is_running = True
        
        try:
            pdf_files = self.get_all_pdfs()
            self.total_pdfs = len(pdf_files)
            
            if self.total_pdfs == 0:
                self.completion_callback(success=True, message="Nenhum PDF encontrado na pasta selecionada.")
                return

            self._report_progress("", 0)
            
            # Número seguro de workers: muitos processos simultâneos causam esgotamento
            # de handles de arquivo no Windows com 500+ PDFs.
            # CPU-bound + I/O: usar no máximo cpu_count workers.
            safe_workers = min(os.cpu_count() or 4, 8)
            with ProcessPoolExecutor(
                max_workers=safe_workers,
                initializer=_worker_initializer,
                initargs=(_filename_lock,)
            ) as executor:
                self._executor = executor  # Salva referência para poder encerrar de fora
                futures = {executor.submit(_process_pdf_worker, pdf_path, os.path.basename(pdf_path), self.search_name, self.search_name_normalized, self.target_dir): pdf_path for pdf_path in pdf_files}
                
                for future in as_completed(futures):
                    pdf_path = futures[future]
                    filename = os.path.basename(pdf_path)
                    
                    if not self.is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                        
                    try:
                        matches_found = future.result()
                        with self.lock:
                            self.processed_pdfs += 1
                            if matches_found > 0:
                                self.total_matches += matches_found
                            self._report_progress(filename, 0)
                    except Exception as e:
                        logger.error(f"Erro ao processar {pdf_path}: {e}")
                        with self.lock:
                            self.processed_pdfs += 1
                            self._report_progress(filename, 0)
                
            if self.is_running:
                self.completion_callback(success=True, message="Busca concluída com sucesso!")
            else:
                self.completion_callback(success=False, message="Busca interrompida pelo usuário.")
                
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            self.completion_callback(success=False, message=f"Erro: {str(e)}")
            
    def stop_search(self, force=False):
        """Para a busca. Se force=True, encerra o pool de processos imediatamente."""
        self.is_running = False
        if force and self._executor is not None:
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
            self._executor = None
        
    def _report_progress(self, current_file, matches_increment):
        progress = self.processed_pdfs / self.total_pdfs if self.total_pdfs > 0 else 0
        
        self.update_callback({
            'total_pdfs': self.total_pdfs,
            'processed_pdfs': self.processed_pdfs,
            'current_file': current_file,
            'total_matches': self.total_matches,
            'progress': progress
        })
