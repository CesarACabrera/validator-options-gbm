import io
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class VisualUtils:
    """Clase para manejar la generación de recursos visuales y LaTeX."""
    
    @staticmethod
    def create_latex_image(latex_string, base_fontsize, scaling_factor):
        """Genera una imagen a partir de una cadena de LaTeX."""
        scaled_fontsize = int(base_fontsize * scaling_factor)
        scaled_dpi = int(100 * scaling_factor)
        
        # Configuramos la figura de matplotlib para renderizar texto
        fig = plt.figure(figsize=(1, 0.5), dpi=scaled_dpi)
        fig.text(0, 0, latex_string, fontsize=scaled_fontsize, va="bottom")
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        
        img = Image.open(buf)
        photo_image = ImageTk.PhotoImage(img)
        plt.close(fig)
        return photo_image