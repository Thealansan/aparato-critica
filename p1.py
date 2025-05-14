import os
import random
import socket
import qrcode
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'fotos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

HTML_QR_ONLY = """
<!DOCTYPE html>
<html>
<head>
    <title>Sube tu imagen desde el celular</title>
    <style>
        body, html {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: sans-serif;
            overflow: hidden;
        }
        .bg-video {
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
            object-fit: cover;
        }
        .content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: white;
            text-shadow: 0 0 10px black;
        }
        img.qr {
            width: 240px;
            margin-top: 20px;
            border: 5px solid white;
            border-radius: 16px;
            background: white;
        }
    </style>
</head>
<body>
    <video class="bg-video" autoplay muted loop playsinline>
        <source src="/static/banner.mp4" type="video/mp4">
        Tu navegador no soporta videos HTML5.
    </video>
    <div class="content">
        <h1>Aparato De Crítica</h1>
        <img class="qr" src="/qr.png" alt="QR de subida" />
    </div>
</body>
</html>
"""

UPLOAD_AND_RANDOM_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subir y ver imágenes</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body, html {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: sans-serif;
            overflow: auto;
        }
        .bg-video {
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
            object-fit: cover;
        }
        .overlay {
            position: relative;
            z-index: 1;
            padding: 20px;
            text-align: center;
            color: white;
            text-shadow: 0 0 8px black;
        }
        h2 {
            font-size: 18px;
            line-height: 1.5;
            margin-bottom: 20px;
            max-width: 90vw;
            margin-left: auto;
            margin-right: auto;
        }
        #uploadForm {
            display: block;
            margin-top: 20px;
        }
        input[type="file"] {
            font-size: 16px;
            margin-bottom: 10px;
        }
        button {
            padding: 8px 16px;
            font-size: 16px;
            background-color: #000;
            color: white;
            border: none;
            border-radius: 8px;
        }
        #gallery {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            justify-items: center;
            margin-top: 20px;
        }
        #gallery img {
            width: 100%;
            max-width: 320px;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        }
        @media (min-width: 600px) {
            #gallery {
                grid-template-columns: repeat(2, 1fr);
                max-width: 700px;
                margin-left: auto;
                margin-right: auto;
            }
        }
    </style>
</head>
<body>
    <video class="bg-video" autoplay muted loop playsinline>
        <source src="/static/banner.mp4" type="video/mp4">
        Tu navegador no soporta videos HTML5.
    </video>
    <div class="overlay">
        <h2>
            Sube una imagen.<br>
            No hay diálogo.<br>
            Sentencia visual.<br>
            La crítica abandona el texto y se encarna en imágenes.<br>
            La tuya es, campo de observación, superficie de juicio, residuo de una conversación unilateral.<br>
            Sentencia visual.<br>
            Sube una imagen.
        </h2>
        <form id="uploadForm" method="POST" enctype="multipart/form-data">
            <input type="file" name="foto" accept="image/*" required><br>
            <button type="submit">Subir</button>
        </form>
        <div id="gallery"></div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const gallery = document.getElementById('gallery');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const html = await response.text();
            gallery.innerHTML = html;
            form.style.display = 'none';

            setTimeout(() => {
                gallery.innerHTML = '';
                form.style.display = 'block';
            }, 30000);
        });
    </script>
</body>
</html>
"""

PHOTO_SNIPPET = """
{% for foto in fotos %}
    <img src="{{ foto }}">
{% endfor %}
"""

@app.route('/')
def index():
    return render_template_string(HTML_QR_ONLY)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        foto = request.files.get('foto')
        if foto:
            filename = foto.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(save_path)

        files = [
            f for f in os.listdir(UPLOAD_FOLDER)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]
        seleccionadas = random.sample(files, 4) if len(files) >= 4 else files
        urls = [f'/static/fotos/{f}' for f in seleccionadas]
        return render_template_string(PHOTO_SNIPPET, fotos=urls)
    else:
        return render_template_string(UPLOAD_AND_RANDOM_PAGE)

@app.route('/qr.png')
def serve_qr():
    ip = get_local_ip()
    url = f"http://{ip}:5000/upload"
    img = qrcode.make(url)
    path = os.path.join(app.root_path, 'static', 'qr.png')
    img.save(path)
    return send_file(path, mimetype='image/png')

if __name__ == '__main__':
    print("Escanea este QR o entra desde tu celular:")
    print(f"http://{get_local_ip()}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)