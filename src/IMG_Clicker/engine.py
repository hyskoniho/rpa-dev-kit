#! Needs paddlepaddle, paddleocr, python-levenshtein, unidecode, easyocr and opencv-python
import pyautogui, Levenshtein, easyocr, os, time, tempfile
from unidecode import unidecode
from paddleocr import PaddleOCR

class Finder():
    def __init__(self) -> None:
        self.engine = PaddleOCR(
            use_angle_cls=True, 
            lang='pt'
        )

    @staticmethod
    def string_treat(string: str) -> str:
        return unidecode(string).strip().lower()

    @staticmethod
    def string_similarity(str1: str, str2: str) -> float:
        distance: float = Levenshtein.distance(str1, str2)
        max_len: int = max(len(str1), len(str2))
        similarity: float = (1 - distance / max_len) * 100
        return similarity

    @staticmethod
    def find_zone(zone_title: str) -> tuple[int]:
        w, h = pyautogui.size()
        
        match zone_title:
            case 'q1':
                return (0, 0, w//2, h//2)
            case 'q2':
                return (w//2, 0, w//2, h//2)
            case 'q3':
                return (0, h//2, w//2, h)
            case 'q4':
                return (w//2, h//2, w, h)
            case 'h1':
                return (0, 0, w, h//2)
            case 'h2':
                return (0, h//2, w, h//2)
            case 'v1':
                return (0, 0, w//2, h)
            case 'v2':
                return (w//2, 0, w//2, h)
            case _:
                raise ValueError("Invalid zone title.")
            
    @staticmethod
    def find_desloc(zone_title: str) -> tuple[int]:
        w, h = pyautogui.size()
        
        match zone_title:
            case 'q1':
                return (0, 0)
            case 'q2':
                return (w//2, 0)
            case 'q3':
                return (0, h//2)
            case 'q4':
                return (w//2, h//2)
            case 'h1':
                return (0, 0)
            case 'h2':
                return (0, h//2)
            case 'v1':
                return (0, 0)
            case 'v2':
                return (w//2, 0)   
            case _:
                raise ValueError("Invalid zone title.") 

    def fbw(self, label: str, zone: tuple[int] = None, similarity: int = 80, str_treat: bool = False, verbose: bool = False) -> tuple:            
        screenshot = pyautogui.screenshot() if not zone else pyautogui.screenshot(region=zone)
        
        try:
            found: bool = False
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                screenshot.save(temp_file.name)
                resultados = self.engine.ocr(temp_file.name, cls=False)
                name: str = temp_file.name
            os.remove(name)
            
            for linha in resultados:
                for info in linha:
                    texto = info[1][0] if not str_treat else self.string_treat(info[1][0])
                    if str_treat: label = self.string_treat(label)
                    sim = self.string_similarity(label, texto)
                    if verbose: print(f'Alvo: \'{label}\' | Texto: \'{texto}\' | Similaridade: {sim}')
                    if label in texto or sim >= similarity:
                        coordenadas = info[0]
                        x = (coordenadas[0][0] + coordenadas[2][0]) / 2
                        y = (coordenadas[0][1] + coordenadas[2][1]) / 2
                        found = True
                        break
                if found: break

        except Exception as e:
            print(e)
            return None
        
        else:
            return (x, y) if found else None
    
    def fbi(self, image_path: str, zone: tuple = None, confidence: float = 0.75, grayscale = True) -> tuple:            
        try:
            element = pyautogui.locateCenterOnScreen(image_path, confidence = confidence, grayscale = grayscale, region = zone)
        
        except Exception as e:
            print(e)
            return None

        else:
            return element
        
def find_element(
        mode: str, 
        elements: tuple[str],
        desloc: tuple[int] = (0, 0), 
        zone: tuple[int] | str = None, 
        force_desloc: tuple[bool] = (False, False), 
        str_similarity: int = 80, 
        str_treat: bool = False, 
        img_confidence: float = 0.75,
        img_grayscale: bool = True,
        ocr_verbose: bool = False, 
        retries: int = 3,
        retry_delay: float = 1.3,
        click: bool = True
    ) -> tuple[int]:
    
    global finder_obj
    
    assert mode in ['ocr', 'img', 'both'], "Invalid mode."
    assert retries >= 0, "Retries must be greater than or equal to 0."
    
    elements: tuple[str] = (elements,) if isinstance(elements, str) else elements
    assert len(elements) > 0, "Element not exists."
    
    img_path: str = ''
    field_label: str = ''
    find_by: str = ''
    
    if mode in ['img', 'both']:
        img_path: str = [e for e in elements if any([e.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']])][0]
        assert img_path, "Image path not found."
        
    if mode in ['ocr', 'both']:
        field_label: str = [e for e in elements if e != img_path][0] if img_path else elements[0]
        assert field_label, "Field label not found."
        
    if zone:
        if isinstance(zone, str):
            zone: tuple[int] = finder_obj.find_zone(zone)
                
        elif isinstance(zone, tuple):
            zone: tuple[int] = tuple(int(z) for z in zone)
    
    if desloc:   
        if isinstance(desloc, str):
            desloc: tuple[int] = finder_obj.find_desloc(desloc)
        else:
            desloc: tuple[int] = tuple(int(d) for d in desloc)
        
    for retry in range(retries):
        try:
            if (mode == 'img' or mode == 'both'):
                locate: tuple[int] = finder_obj.fbi(
                    image_path = img_path, 
                    zone = zone, 
                    confidence = img_confidence, 
                    grayscale = img_grayscale
                )
                if locate: 
                    find_by: str = 'img'
            
            if mode == 'ocr' or (mode == 'both' and not locate):
                locate: tuple[int] = finder_obj.fbw(
                    label = field_label, 
                    zone = zone, 
                    similarity = str_similarity, 
                    str_treat = str_treat,
                    verbose = ocr_verbose 
                )  
                if locate: 
                    find_by: str = 'ocr'
            
            if locate:
                locate: tuple[int] = (
                    locate[0] + (desloc[0] if find_by == 'ocr' or force_desloc[0] else 0),
                    locate[1] + (desloc[1] if find_by == 'ocr' or force_desloc[1] else 0)
                )
                
                if click:
                    pyautogui.click(locate[0], locate[1])
                
                return locate

            else:
                raise Exception("Element not found.")
    
        except:
            if not retry: 
                return None
            else:
                time.sleep(retry_delay + retry)

if not globals().get('finder_obj', None):
    finder_obj = Finder()

if __name__ == '__main__':
    from ptymer import Timer
    with Timer(visibility=True) as t:
        coordenadas = find_element(mode="img", elements=r"assets\Captura de tela 2025-04-21 161456.png", zone="q1")
        if coordenadas:
            print(f"A palavra foi encontrada nas coordenadas: {coordenadas}")
            pyautogui.moveTo(coordenadas)
        else:
            print("A palavra não foi encontrada.")