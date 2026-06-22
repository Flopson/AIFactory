AI Factory

Automatyczny generator filmów AI.

Uruchomienie:

    ComfyUI:
        cd C:\AIFactory\image_ai\ComfyUI
        ..\venv\Scripts\activate
        python main.py --directml

    Ollama:
        ollama list
        ollama pull llama3.1:8b

    cd C:\AIFactory
    python run_pipeline.py

Pipeline:

script
↓
scene split
↓
director
↓
audio
↓
images
↓
video

Output:

output/final.mp4