# Comandos

- Entrar a una carpeta

    cd nombre_carpeta

- Regresar a una carpeta

    cd ..

- Ver archivos

    dir


# Git y GitHub

Inicializar git 
    git init

Ver estado del proyecto 

    git status

Ver ramas

    git branch

Cambiar de rama

    git checkout nombre_rama

Agregar archivos 

    git add .

    git commit -m "mensaje de cambios realizados"

    git push origin dev

## Aplicar este comando antes de trabajar (Actualizar)
    git pull origin dev

# Levantar backend
    cd backend
        .\.venv\Scripts\Activate.ps1


## Cómo correr el proyecto en desarrollo

Terminal 1 (backend):
cd backend
python -m uvicorn app.main:app --reload

Terminal 2 (frontend):
cd frontend
python -m http.server 3000

Abrir en navegador: http://localhost:3000