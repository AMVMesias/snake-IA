import matplotlib.pyplot as plt
from IPython import display

# Configurar un estilo más atractivo pero manteniendo todo lo demás igual
plt.style.use('dark_background')

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    
    # Fondo y estilo mejorados
    ax = plt.gca()
    ax.set_facecolor('#1E1E1E')  # Fondo más oscuro
    
    # Títulos mejorados pero con el mismo texto
    plt.title('Training...', color='white', fontsize=14)
    plt.xlabel('Number of Games', color='white')
    plt.ylabel('Score', color='white')
    
    # Usar colores más atractivos para las líneas
    plt.plot(scores, color='#00CFFF')  # Azul brillante
    plt.plot(mean_scores, color='#FF5757')  # Rojo coral
    
    # Mantener el mismo límite del eje Y
    plt.ylim(ymin=0)
    
    # Mejorar la visualización de los valores pero mantener la misma lógica
    if len(scores) > 0:
        plt.text(len(scores)-1, scores[-1], str(scores[-1]), color='#00CFFF')
    if len(mean_scores) > 0:
        plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]), color='#FF5757')
    
    # Una cuadrícula sutil para mejorar la visualización
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Mantener exactamente las mismas llamadas originales
    plt.show(block=False)
    plt.pause(.1)