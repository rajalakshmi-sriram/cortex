# Cortex macOS App - Build & Distribution Guide

## Overview

This guide explains how to package and distribute Cortex as a native macOS application that can be uploaded to the Mac App Store or distributed directly.

## What's Included

The macOS app packaging includes:

1. **PyQt6 GUI Application** - Native macOS interface
2. **Automatic Server Management** - Starts Cortex backend automatically
3. **App Bundle** - Proper macOS .app format
4. **DMG Installer** - Professional distribution format
5. **Code Signing** - Optional code signing for distribution

## Building the macOS App

### Prerequisites

```bash
# Ensure you have:
- macOS 10.13 or later
- Python 3.8 or later
- Xcode Command Line Tools (for code signing)
```

### Step 1: Update Requirements

The additional PyQt6 dependency has been added to `requirements.txt`:

```bash
# Run this in the cortex directory
pip install PyQt6 PyQt6-WebEngine py2app
```

### Step 2: Build the App

```bash
cd /Users/rajalakshmisriram/cortex

# Make build script executable and run it
chmod +x build_macos_app.sh
./build_macos_app.sh
```

This will:
1. Create a Python virtual environment
2. Install all dependencies
3. Build the app bundle using py2app
4. Code sign the app (if certificate available)
5. Create a DMG installer

### Step 3: Test the App

```bash
# Run the app directly
open dist/Cortex.app

# Or use the DMG
open dist/Cortex-1.0.0.dmg
```

## What Happens When You Run the App

1. **Launch** - User opens Cortex.app from Applications
2. **Backend Start** - App automatically starts the Cortex Flask server
3. **Connection** - GUI connects to local server (localhost:5000)
4. **Interface** - User sees the PyQt6 interface with 4 tabs:
   - Validate Idea
   - Research Modes
   - Get Methodology
   - Documentation

## App Structure

```
Cortex.app/
├── Contents/
│   ├── MacOS/
│   │   └── Cortex          (Executable entry point)
│   ├── Resources/
│   │   ├── __boot__.py
│   │   ├── cortex_gui.py
│   │   ├── run.py
│   │   ├── config/
│   │   ├── app/
│   │   └── ...
│   ├── Frameworks/         (Python and libraries)
│   └── Info.plist          (App metadata)
```

## Mac App Store Distribution

To distribute on the Mac App Store:

### 1. Get an Apple Developer Account

- Visit https://developer.apple.com/
- Enroll in Apple Developer Program ($99/year)
- Create App ID for Cortex

### 2. Prepare for App Store

```bash
# Create App Store specific build
# Update app ID in setup.py to match your registered ID
# com.cortex-research.cortex → your-actual-id

# Important: Mac App Store requires specific entitlements
```

### 3. Create App Store Configuration

File: `macos-app/entitlements-appstore.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.developer.networking.local-outbound</key>
	<true/>
	<key>com.apple.developer.networking.multicast</key>
	<true/>
	<key>com.apple.security.app-sandbox</key>
	<true/>
</dict>
</plist>
```

### 4. Create Distribution Package

```bash
# Create signed DMG for App Store submission
productbuild --component dist/Cortex.app /Applications \
  --sign "3rd Party Mac Developer Installer" \
  dist/Cortex-AppStore.pkg
```

### 5. Submit to App Store

- Sign in to App Store Connect
- Create new app entry
- Upload `.pkg` file
- Submit for review

## Direct Distribution

For direct distribution (without Mac App Store):

### Option 1: DMG File (Recommended)

The build script automatically creates:
```
dist/Cortex-1.0.0.dmg
```

Users can:
1. Download DMG
2. Open DMG
3. Drag Cortex to Applications folder
4. Launch from Applications

### Option 2: ZIP Archive

```bash
cd dist
zip -r Cortex-1.0.0.zip Cortex.app
```

Users can:
1. Download ZIP
2. Unzip automatically
3. Move to Applications
4. Launch

### Option 3: Code Signing for Direct Distribution

```bash
# Create certificate request
# Go to: https://developer.apple.com/account/resources/certificates

# Get your certificate ID
CERT_ID="YOUR_CERTIFICATE_ID"

# Sign the app
codesign --deep --force --verify --verbose \
  --sign "$CERT_ID" \
  dist/Cortex.app

# Verify signature
codesign --verify --verbose dist/Cortex.app
```

## Hosting Options

### GitHub Releases

```bash
# Create release with DMG attached
# Users download directly from GitHub
gh release create v1.0.0 dist/Cortex-1.0.0.dmg
```

### Website Hosting

```bash
# Host DMG on your website
# Users download from cortex-research.com/download
```

### Mac App Store

```bash
# Official Apple distribution
# Users find in Mac App Store
# Apple handles payment and distribution
```

## File Structure for Distribution

```
Before Distribution:
├── dist/
│   ├── Cortex.app          (Production app)
│   └── Cortex-1.0.0.dmg    (Installer)
├── build/                  (Build artifacts - can delete)
└── venv-build/            (Build venv - can delete)

For Release:
├── Cortex-1.0.0.dmg       (Upload to distribution channel)
└── Cortex-1.0.0.zip       (Alternative distribution)
```

## Troubleshooting

### App Won't Start

```bash
# Check app logs
log stream --predicate 'processImagePath contains "Cortex"'

# Run with debug info
open -a Console dist/Cortex.app
```

### Server Connection Issues

```bash
# Check if port 5000 is available
lsof -i :5000

# Restart server manually
python run.py
```

### Code Signing Issues

```bash
# List available certificates
security find-identity -v -p codesigning

# Remove invalid signature
codesign --remove-signature dist/Cortex.app

# Sign with correct certificate
codesign --deep --force --sign "CERTIFICATE_ID" dist/Cortex.app
```

### PyQt6 Issues

```bash
# Clear cache and rebuild
rm -rf build dist venv-build
./build_macos_app.sh
```

## App Bundle Contents

The built app includes:

### Python Runtime
- Full Python 3.x distribution
- All required packages bundled

### Cortex Backend
- Flask server
- NLP engine
- Literature fetcher
- Methodology engine
- Configuration

### GUI Application
- PyQt6 interface
- 4 main tabs
- Real-time API communication

### Resources
- App icons
- Configuration files
- Documentation

## Size Expectations

```
App Size: ~200-300 MB (includes Python + PyQt6)
DMG Size: ~100-150 MB (compressed)
```

## Updating the App

When releasing updates:

```bash
# Version 1.0.1
1. Update version in setup.py
2. Run build script
3. Create new DMG
4. Upload to distribution channel
```

## Security Considerations

### Notarization (macOS 10.15+)

For apps distributed outside Mac App Store:

```bash
# Submit app for notarization
xcrun altool --notarize-app \
  --file dist/Cortex-1.0.0.dmg \
  --primary-bundle-id com.cortex-research.cortex \
  -u your-apple-id@example.com \
  -p your-app-specific-password

# Staple notarization
xcrun stapler staple dist/Cortex.app
```

### Gatekeeper Handling

Users may see security warnings:

```
"Cortex" cannot be opened because the developer cannot be verified.
```

To fix:
1. Right-click on Cortex.app
2. Select "Open"
3. Click "Open" in security dialog

Or use: `xattr -d com.apple.quarantine dist/Cortex.app`

## Distribution Checklist

- [ ] App builds successfully
- [ ] App launches without errors
- [ ] All 4 tabs functional
- [ ] Server starts automatically
- [ ] Code is signed (optional)
- [ ] DMG created successfully
- [ ] DMG tested on different Mac
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] Release notes prepared

## Next Steps

### For Mac App Store:
1. Create Apple Developer account
2. Register app ID
3. Build with App Store entitlements
4. Submit for review
5. Wait for approval

### For Direct Distribution:
1. Test the DMG thoroughly
2. Host on website or GitHub
3. Create download page
4. Share with users
5. Collect feedback

### For Future Updates:
1. Update version number
2. Run build script
3. Create new DMG
4. Test thoroughly
5. Release to users

## Support Resources

### Apple Resources
- [App Distribution Guide](https://help.apple.com/app-store-connect/)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Notarization Guide](https://developer.apple.com/documentation/notaryapi)

### PyQt6 Resources
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [py2app Guide](https://py2app.readthedocs.io/)

### Cortex Resources
- [Cortex README](README.md)
- [Quick Start](QUICKSTART.md)
- [Project Summary](PROJECT_SUMMARY.md)

## Legal Requirements

When distributing on Mac App Store:

1. **Privacy Policy** - Required
2. **Terms of Service** - Recommended
3. **Licensing** - Specify (MIT, Apache, etc.)
4. **Permissions** - Document what app accesses
5. **EULA** - End User License Agreement

## Files Modified/Created for macOS Support

```
New Files:
├── cortex_gui.py                  (PyQt6 GUI application)
├── setup.py                       (py2app configuration)
├── build_macos_app.sh             (Build automation)
└── macos-app/
    ├── Info.plist                 (App metadata)
    ├── entitlements.plist         (Permissions)
    └── cortex_launcher.sh         (Launch script)

Modified Files:
└── requirements.txt               (Added PyQt6, py2app)
```

## Version History

### v1.0.0 (Current)
- Initial macOS app release
- PyQt6 GUI interface
- Automatic server management
- DMG installer
- Code signing support

### Future Versions
- Mac App Store distribution
- Auto-update mechanism
- Notification system
- Advanced settings panel

---

## Quick Reference Commands

```bash
# Build the app
./build_macos_app.sh

# Run the app
open dist/Cortex.app

# Test the DMG
open dist/Cortex-1.0.0.dmg

# Clean build artifacts
rm -rf build dist venv-build

# Check code signature
codesign --verify --verbose dist/Cortex.app

# Rebuild from scratch
rm -rf build dist venv-build *.dmg
./build_macos_app.sh
```

---

**Ready to distribute Cortex as a native macOS application!** 🍎
