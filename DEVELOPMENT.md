# GiffyDrop - Development Notes

## Project Principles
- Clean, production-ready code
- Full type hints for IDE support
- English comments and docstrings
- Modular OOP architecture
- UI-agnostic backend logic

## Key Design Decisions

### Why Two-Pass Palette Method?
The two-pass method generates a custom color palette optimized for each video, resulting in significantly better quality than direct conversion. This is crucial for Discord users who want their GIFs to look professional.

### Why Threading?
FFmpeg operations can take several seconds to minutes depending on video length. Running conversions in a separate thread prevents the GUI from freezing, providing a better user experience.

### Why CustomTkinter?
- Modern, clean aesthetics matching Discord's dark theme
- Easy to customize and theme
- Better looking than standard Tkinter
- Active development and community

## FFmpeg Command Breakdown

### Pass 1: Palette Generation
```bash
ffmpeg -i input.mp4 \
  -vf "fps=20,scale=320:-1:flags=lanczos,palettegen" \
  -y palette.png
```
- `fps=20`: Reduces frame rate to 20 fps
- `scale=320:-1`: Scales to 320px width, maintains aspect ratio
- `flags=lanczos`: High-quality scaling algorithm
- `palettegen`: Generates optimized color palette

### Pass 2: GIF Creation
```bash
ffmpeg -i input.mp4 -i palette.png \
  -lavfi "fps=20,scale=320:-1:flags=lanczos [x]; [x][1:v] paletteuse" \
  -y output.gif
```
- `[x]`: Stores scaled video in variable
- `[x][1:v] paletteuse`: Applies custom palette to scaled video

## Future Enhancement Ideas
- Batch conversion support
- Real-time file size preview
- Custom output directory selection
- Dithering options (bayer, floyd_steinberg, sierra2_4a)
- Compression level slider
- Video preview window
- Drag-and-drop file input
- Recent files history
- Export presets management
- Progress bar with percentage
- Cancel operation mid-conversion
