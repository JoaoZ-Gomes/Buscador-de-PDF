import os
import glob
import logging
from pypdf import PdfReader, PdfWriter
from utils import normalize_text, get_unique_filename

logger = logging.getLogger(__name__)

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
            
            for pdf_path in pdf_files:
                if not self.is_running:
                    break
                
                filename = os.path.basename(pdf_path)
                self._report_progress(filename, 0)
                
                try:
                    self._process_single_pdf(pdf_path, filename)
                except Exception as e:
                    logger.error(f"Erro ao processar {pdf_path}: {e}")
                
                self.processed_pdfs += 1
                self._report_progress(filename, 0)
                
            if self.is_running:
                self.completion_callback(success=True, message="Busca concluída com sucesso!")
            else:
                self.completion_callback(success=False, message="Busca interrompida pelo usuário.")
                
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            self.completion_callback(success=False, message=f"Erro: {str(e)}")
            
    def _process_single_pdf(self, pdf_path, filename):
        try:
            reader = PdfReader(pdf_path)
            
            if reader.is_encrypted:
                logger.warning(f"Ignorando PDF protegido por senha: {pdf_path}")
                return
                
            found_pages = []
            
            for page_num in range(len(reader.pages)):
                if not self.is_running:
                    break
                    
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    normalized_text = normalize_text(text)
                    if self.search_name_normalized in normalized_text:
                        found_pages.append(page_num)
                        
            for page_num in found_pages:
                if not self.is_running:
                    break
                    
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                base_name = os.path.splitext(filename)[0]
                safe_search_name = "".join(x for x in self.search_name if x.isalnum() or x in " _-")
                safe_search_name = safe_search_name.strip().replace(" ", "_")
                
                new_filename = f"{base_name}_pagina{page_num + 1}_{safe_search_name}.pdf"
                new_filename = get_unique_filename(self.target_dir, new_filename)
                
                output_path = os.path.join(self.target_dir, new_filename)
                
                with open(output_path, "wb") as output_pdf:
                    writer.write(output_pdf)
                
                self.total_matches += 1
                self._report_progress(filename, 1)
                
        except Exception as e:
            logger.error(f"Erro ao ler/escrever o PDF {pdf_path}: {e}")

    def stop_search(self):
        self.is_running = False
        
    def _report_progress(self, current_file, matches_increment):
        progress = self.processed_pdfs / self.total_pdfs if self.total_pdfs > 0 else 0
        
        self.update_callback({
            'total_pdfs': self.total_pdfs,
            'processed_pdfs': self.processed_pdfs,
            'current_file': current_file,
            'total_matches': self.total_matches,
            'progress': progress
        })
