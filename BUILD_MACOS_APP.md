# Cortex macOS App - Complete Build & Distribution Guide

## 🎯 Quick Overview

You now have **Cortex** ready to be packaged as a native macOS application with:

✅ **PyQt6 GUI** - Professional native interface  
✅ **Automatic Backend** - Flask server starts automatically  
✅ **Easy Installation** - DMG installer for users  
✅ **App Store Ready** - Can be submitted to Mac App Store  

---

## 📋 Prerequisites

Before you start, ensure you have:

```bash
# Check Python version (need 3.8+)
python3 --version

# Check if you have Xcode Command Line Tools (optional, for signing)
xcode-select --install
```

---

## 🚀 Step 1: Build the macOS App (10 minutes)

### Navigate to Project Directory

```bash
cd /Users/rajalakshmisriram/cortex
```

### Run the Build Script

```bash
# Make script executable (only needed first time)
chmod +x build_macos_app.sh

# Run the build script
./build_macos_app.sh
```

This will automatically:
1. ✓ Create a build virtual environment
2. ✓ Install all dependencies (Flask, PyQt6, etc.)
3. ✓ Create the app bundle
4. ✓ Code sign (if certificate available)
5. ✓ Create a DMG installer

### Expected Output

```
✓ Virtual environment ready
✓ Dependencies installed
✓ App bundle created
✓ DMG created: dist/Cortex-1.0.0.dmg
```

---

## 📦 Step 2: Test the App (5 minutes)

### Option A: Run from Build Directory

```bash
open dist/Cortex.app
```

### Option B: Install from DMG

```bash
# Open the DMG
open dist/Cortex-1.0.0.dmg

# Drag Cortex.app to Applications folder
# Or use terminal:
cp -r dist/Cortex.app /Applications/Cortex.app

# Launch from Applications
open /Applications/Cortex.app
```

### What You Should See

When you launch the app:

1. **Splash Screen** - "Cortex - Brain Research Methodology Platform"
2. **4 Tabs** - At the top:
   - Validate Idea
   - Research Modes
   - Get Methodology
   - Documentation
3. **Status Bar** - Shows "✓ Server Running" if backend is active

### Try These Functions

**Tab 1: Validate Idea**
- Enter: "Study memory consolidation in aging mice"
- Click: "Validate Idea"
- See: Similarity score and related papers

**Tab 2: Research Modes**
- Browse: 10 different research methodologies
- Read: Mode descriptions and details

**Tab 3: Get Methodology**
- Enter your idea
- Select a research mode
- Click: "Get Methodology Guidance"
- See: 15-25 sequential steps

**Tab 4: Documentation**
- Links to guides and resources
- About information

---

## 🔧 Step 3: Code Signing (Optional but Recommended)

### Check Available Certificates

```bash
# List all code signing certificates
security find-identity -v -p codesigning
```

### Sign the App

If you have a Developer ID certificate:

```bash
# Replace CERTIFICATE_ID with the one from above
CERT_ID="XXXXXXXXXXXXXXXXXX"

codesign --deep --force --sign "$CERT_ID" dist/Cortex.app

# Verify signature
codesign --verify --verbose dist/Cortex.app
```

### Without a Certificate

Users will see a security warning on first launch:
- They can right-click and select "Open"
- Or run: `xattr -d com.apple.quarantine /Applications/Cortex.app`

---

## 📤 Step 4: Distribution Options

### Option A: Direct Download (GitHub)

**Host on GitHub:**

```bash
# Create a release on GitHub
gh release create v1.0.0 dist/Cortex-1.0.0.dmg

# Users download: cortex-research/releases/v1.0.0
```

**Users install:**
1. Download `Cortex-1.0.0.dmg`
2. Open DMG
3. Drag Cortex to Applications
4. Launch

### Option B: Website Download

**Host on Your Website:**

```bash
# Create download page at cortex-research.com/download
# Users download DMG file directly
```

### Option C: Mac App Store

**For App Store Distribution:**

1. **Register with Apple Developer Program**
   - Visit: https://developer.apple.com/
   - Cost: $99/year
   - Create App ID: `com.yourcompany.cortex`

2. **Create App Store Configuration**
   - Update `setup.py` with your App ID
   - Create entitlements file

3. **Build for App Store**
   ```bash
   # We'll provide App Store build script
   ./build_macos_app_appstore.sh
   ```

4. **Submit to App Store**
   - Use App Store Connect
   - Upload the build
   - Fill in metadata (screenshots, description)
   - Submit for review

### Option D: Direct Installation

**For testing and small distribution:**

```bash
# Just copy the app
cp -r dist/Cortex.app /Applications/

# Users launch from Applications folder
open /Applications/Cortex.app
```

---

## 📝 Step 5: Create Distribution Package

### Create ZIP for Alternative Distribution

```bash
cd dist
zip -r Cortex-1.0.0.zip Cortex.app
```

Users can:
- Download ZIP
- Auto-unzip on Mac
- Move to Applications
- Launch

### Create Multiple Formats

```bash
cd dist

# ZIP for GitHub/website
zip -r Cortex-1.0.0.zip Cortex.app

# DMG already created
ls -lh Cortex-1.0.0.dmg

# TAR.GZ for Linux users who might want source
tar -czf Cortex-1.0.0.tar.gz Cortex.app
```

---

## 🌐 Step 6: Publish & Share

### GitHub Releases

```bash
# Create release with DMG attached
gh release create v1.0.0 \
  dist/Cortex-1.0.0.dmg \
  dist/Cortex-1.0.0.zip \
  -t "Cortex v1.0.0" \
  -n "Initial release - Brain Research Methodology Platform"
```

### Website

```html
<!-- Example HTML for download page -->
<h1>Download Cortex</h1>
<p>macOS Application for Brain Research</p>

<a href="/downloads/Cortex-1.0.0.dmg">
  Download Cortex v1.0.0 (DMG - 120 MB)
</a>

<p>Requirements: macOS 10.13 or later</p>
```

### Social Media

```
🎉 Excited to announce Cortex v1.0.0!

An intelligent platform for brain research methodology.

✨ Validate research ideas
✨ Select from 10 research methodologies
✨ Get step-by-step guidance
✨ Search 39 neuroscience sources

Download now: [link to DMG]

#neuroscience #research #brainsci
```

---

## 📊 File Structure After Build

```
After Building:

cortex/
├── dist/
│   ├── Cortex.app                    ← The application
│   ├── Cortex-1.0.0.dmg              ← DMG installer
│   └── Cortex-1.0.0.zip              ← ZIP alternative
├── build/                            ← Build artifacts
├── venv-build/                       ← Build environment
│
├── cortex_gui.py                     ← GUI source code
├── setup.py                          ← Build configuration
├── build_macos_app.sh                ← Build automation
│
└── ... (rest of Cortex application)
```

---

## 🔧 Troubleshooting

### App Won't Launch

**Check System Logs:**
```bash
log stream --predicate 'processImagePath contains "Cortex"'
```

**Common Issues:**
- Port 5000 in use: `lsof -i :5000` and kill process
- Missing dependencies: Run build script again
- Permission issues: Check file permissions

### Server Not Starting

```bash
# Manually start server
python run.py

# In another terminal, test connection
curl http://localhost:5000/health
```

### GUI Issues

```bash
# Clear PyQt6 cache
rm -rf ~/.cache/PyQt6*

# Rebuild
rm -rf build dist venv-build
./build_macos_app.sh
```

### Code Signing Errors

```bash
# Remove existing signature
codesign --remove-signature dist/Cortex.app

# Try signing again
codesign --deep --force --sign "CERT_ID" dist/Cortex.app

# Verify
codesign --verify --verbose dist/Cortex.app
```

---

## 📈 Version Management

When releasing updates:

### Update Version Number

```bash
# In setup.py
# Change: 'CFBundleVersion': '1.0.0' → '1.0.1'

# In MACOS_APP_GUIDE.md
# Update all references to 1.0.0 → 1.0.1
```

### Rebuild for New Version

```bash
# Clean
rm -rf build dist venv-build

# Rebuild
./build_macos_app.sh

# Test
open dist/Cortex.app

# Publish new DMG
gh release create v1.0.1 dist/Cortex-1.0.1.dmg
```

---

## 🔐 Security & Notarization

For macOS 10.15+ (Big Sur and later):

### Notarize Your App

```bash
# This requires Apple Developer account

# Notarize the app
xcrun altool --notarize-app \
  --file dist/Cortex-1.0.0.dmg \
  --primary-bundle-id com.cortex-research.cortex \
  -u your-apple-id@example.com \
  -p your-app-specific-password
```

### Check Notarization Status

```bash
xcrun altool --notarization-info REQUEST_UUID \
  -u your-apple-id@example.com \
  -p your-app-specific-password
```

### Staple Notarization

```bash
xcrun stapler staple dist/Cortex.app
```

---

## 📋 Checklist Before Release

- [ ] Build script runs without errors
- [ ] App launches successfully
- [ ] All 4 tabs are functional
- [ ] Backend server starts automatically
- [ ] API calls return correct results
- [ ] DMG installs correctly
- [ ] App runs from Applications folder
- [ ] Code is signed (optional)
- [ ] Release notes written
- [ ] Version number updated
- [ ] Documentation updated
- [ ] Tested on different Mac if possible

---

## 🎯 Distribution Checklist

**Before publishing:**

- [ ] Create GitHub release
- [ ] Upload DMG and ZIP files
- [ ] Create download page on website
- [ ] Test download links work
- [ ] Write release notes
- [ ] Announce on social media
- [ ] Send to colleagues for testing
- [ ] Collect feedback

**For Mac App Store:**

- [ ] Create Apple Developer account
- [ ] Register App ID
- [ ] Create screenshots
- [ ] Write app description
- [ ] Set pricing (free or paid)
- [ ] Submit build
- [ ] Answer review questions
- [ ] Wait for approval

---

## 🆘 Support Commands

```bash
# Check app info
ls -lh dist/Cortex.app

# Check app bundle structure
du -sh dist/Cortex.app

# Test launch
open -v dist/Cortex.app

# Check logs
log stream --predicate 'processImagePath contains "Cortex"' --level debug

# Kill running instances
killall -9 Cortex

# Rebuild everything
rm -rf build dist venv-build *.dmg
./build_macos_app.sh

# List all files in app
find dist/Cortex.app -type f | wc -l
```

---

## 📚 Next Steps

### Immediate (Today)
1. ✓ Run `./build_macos_app.sh`
2. ✓ Test `open dist/Cortex.app`
3. ✓ Try all 4 tabs

### This Week
1. ✓ Create GitHub release
2. ✓ Create download page
3. ✓ Get feedback from testers

### This Month
1. ✓ Polish GUI based on feedback
2. ✓ Create App Store account (if interested)
3. ✓ Submit to App Store (if interested)

### Ongoing
1. ✓ Update as Cortex develops
2. ✓ Release new versions
3. ✓ Monitor feedback and issues

---

## 📞 Support Resources

**Cortex Documentation:**
- README.md - Complete reference
- QUICKSTART.md - Getting started
- PROJECT_SUMMARY.md - Architecture
- MACOS_APP_GUIDE.md - App details

**Apple Resources:**
- [App Distribution](https://help.apple.com/app-store-connect/)
- [Code Signing](https://developer.apple.com/support/code-signing/)
- [Notarization](https://developer.apple.com/documentation/notaryapi)

**PyQt6 Resources:**
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [py2app Guide](https://py2app.readthedocs.io/)

---

## 🎉 You're Ready!

Your Cortex macOS application is ready to be built, tested, and distributed!

**Quick Command Summary:**

```bash
# Build
./build_macos_app.sh

# Test
open dist/Cortex.app

# Release (GitHub)
gh release create v1.0.0 dist/Cortex-1.0.0.dmg

# That's it! 🎉
```

---

**Questions?** Check MACOS_APP_GUIDE.md for more details or review the Cortex documentation.

**Ready to ship Cortex to macOS users! 🚀**
