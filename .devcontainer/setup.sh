echo "Setting up backend..."
cd backend

uv python install 3.11
uv python pin 3.11
uv venv --python 3.11

uv sync
uv run pre-commit install
cd ..

echo "Backend setup complete"

echo "Setting up frontend..."
cd frontend

if [ ! -f package.json ]; then
  pnpm dlx sv create .
fi

pnpm install

if ! grep -q '"tailwindcss"' package.json; then
  pnpm add -D tailwindcss @tailwindcss/vite
  npx tailwindcss init -p
  printf '@import "tailwindcss";\n' > src/app.css
fi
cd ..

echo "Setup complete"