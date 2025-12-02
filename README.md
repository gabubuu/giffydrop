# giffydrop

a tool to make discord gifs from mp4 videos. it's basically ffmpeg with a nice gui so you don't have to remember command line stuff.

![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![works on](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

so basically, you have a video that's already edited and trimmed, and you need to turn it into a gif for discord that doesn't exceed the 9.9MB limit. this tool does that without destroying the quality.

## what it does

- keeps gifs under 9.9MB (discord's limit)
- two-pass encoding (fancy ffmpeg stuff to make it look good)
- dark mode ui that doesn't hurt your eyes
- two profiles: one for avatar pics, one for banners
- tells you if your gif is too big and why
- threaded so the app doesn't freeze while converting

## you'll need

- **ffmpeg**: basically the engine that does all the heavy lifting

### setup ffmpeg

on windows:
```powershell
choco install ffmpeg
```

or just download it from https://ffmpeg.org/download.html

on mac:
```bash
brew install ffmpeg
```

on linux (ubuntu/debian):
```bash
sudo apt install ffmpeg
```

## install

1. clone this
   ```bash
   git clone https://github.com/gabubuu/giffydrop.git
   cd giffydrop
   ```

2. make a venv (optional but recommended)
   ```bash
   python -m venv venv
   
   # on windows
   .\venv\Scripts\activate
   
   # on mac/linux
   source venv/bin/activate
   ```

3. get the dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. run it
   ```bash
   python main.py
   ```

## how to use it

1. open the app
2. pick your mp4 video
3. choose profile avatar (320x auto) or profile banner (600x auto)
4. adjust fps if you want (default is 20 for avatar, 15 for banner)
5. click convert
6. wait and watch the log
7. gif appears in `output/` folder

## profiles

### avatar
- fixed at 320x auto (maintains aspect ratio)
- 20 fps by default (but you can change it)
- good for profile pictures

### banner  
- fixed at 600x auto
- 15 fps by default (saves space)
- good for server banners

## fps options

- 30 fps: smooth motion but bigger file
- 24 fps: cinema quality
- 20 fps: sweet spot (marked as balanced)
- 15 fps: smaller file, slight stuttering
- 10 fps: tiny file, very choppy

## how it works internally

it uses ffmpeg's two-pass palette method. basically:

1. **pass 1**: analyzes the video and creates an optimized color palette
2. **pass 2**: makes the gif using that palette

this gives way better quality than just direct conversion because it picks the best colors for your specific video instead of using a generic palette.

## output

your gif goes in `output/` folder wherever your video is. the filename is something like `video_name_optimized.gif`.

if it's over 9.9MB, the app warns you so you know to either:
- lower the fps
- pick a smaller profile
- trim the video more

## code stuff

- python 3.10+
- customtkinter for the gui (dark mode)
- subprocess to run ffmpeg
- threading so it doesn't freeze
- type hints everywhere

the code is pretty straightforward if you want to mess with it. main class is `GiffyConverter` which handles all the ffmpeg stuff, then `App` is the gui.

## troubleshooting

### ffmpeg not found
make sure it's installed and in your PATH. test it with:
```bash
ffmpeg -version
```

### gif is too big
- lower the fps
- use the smaller profile
- trim your video down more in your editor

### it's slow
yeah, two-pass encoding takes time. bigger videos take longer. that's normal.

## license

MIT - do whatever you want with it

---

made because constantly running ffmpeg commands is annoying
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🐛 Troubleshooting

### "FFmpeg not found in PATH"
- Ensure FFmpeg is installed correctly
- Verify it's in your system PATH by running `ffmpeg -version` in terminal
- On Windows, you may need to restart your terminal/IDE after installation

### "File exceeds Discord limit (9.9MB)"
- Try reducing the FPS (e.g., from 20 to 15 or 10)
- Select a smaller width option
- Consider trimming your video further in an external editor

### GUI appears blurry on Windows
- Right-click `python.exe` → Properties → Compatibility → Change high DPI settings
- Check "Override high DPI scaling behavior"

### Conversion is slow
- This is normal for high-quality two-pass encoding
- The status log shows real-time progress
- Larger videos take proportionally longer

## 🙏 Acknowledgments

- **FFmpeg**: The powerful multimedia framework that makes this possible
- **CustomTkinter**: Modern and customizable tkinter UI library
- **Discord**: For being the awesome platform this tool serves

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/giffydrop/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/giffydrop/discussions)

---

<p align="center">Made with ❤️ for the Discord community</p>
