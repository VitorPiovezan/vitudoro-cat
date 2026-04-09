# Vitudoro Cat

Pet virtual com pomodoro para Linux. Um gatinho pixel art que anda pela sua tela e te lembra de descansar.

Inspirado no [Gnomelets](https://github.com/ihpled/gnomelets) - sprites do kitten usados com creditos ao projeto original.

## O que faz

- Gatinho anda, pula e fica idle na parte de baixo da tela
- Suporte a multi-monitor
- Arrastar o gato com o mouse (clique esquerdo)
- Pomodoro configuravel (minutos e segundos)
- Quando o timer dispara:
  - Aparece um balao com mensagem aleatoria
  - O gato pula ate o mouse e puxa o cursor pra baixo
  - Clique direito no gato para parar a perseguicao
  - Apos 10s ele pausa, espera 4s e repete ate voce parar
- Mensagens de pausa customizaveis
- Tamanho do gato ajustavel
- Tray icon com countdown do pomodoro

## Requisitos

- Linux (testado no Zorin OS)
- Python 3.8+
- GTK 3 (PyGObject)

## Instalacao das dependencias

```bash
# Ubuntu/Zorin/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3

# Arch
sudo pacman -S python-gobject gtk3
```

## Como rodar

```bash
git clone https://github.com/VitorPiovezan/vitudoro-cat.git
cd vitudoro-cat
python3 -m vitudoro_cat.main
```

## Instalar como aplicativo

```bash
chmod +x install.sh
./install.sh
```

Depois e so rodar `vitudoro-cat` ou encontrar "Vitudoro Cat" no menu de aplicativos.

## Controles

- Clique esquerdo no gato: arrastar
- Clique direito no gato: abrir configuracoes (ou parar perseguicao se ativa)
- Tray icon (bandeja do sistema): clique pra configuracoes, botao direito pro menu

## Sprites

- 0-3: animacao de andar
- 4: idle (sentado)
- 5: pulo/queda
- 6-7: sendo arrastado
- 8-9: segurando o mouse (custom)
