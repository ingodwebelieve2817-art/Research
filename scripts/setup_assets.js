const fs = require('fs');
const path = require('path');

const srcCss = path.join(__dirname, '..', 'node_modules', 'bootstrap-icons', 'font', 'bootstrap-icons.css');
const srcFontsDir = path.join(__dirname, '..', 'node_modules', 'bootstrap-icons', 'font', 'fonts');

const destCssDir = path.join(__dirname, '..', 'static', 'css');
const destFontsDir = path.join(__dirname, '..', 'static', 'css', 'fonts'); // bootstrap-icons expects font files relative to CSS file, i.e., in './fonts/' relative to bootstrap-icons.css

// Create destination directories if they don't exist
if (!fs.existsSync(destCssDir)) {
  fs.mkdirSync(destCssDir, { recursive: true });
}
if (!fs.existsSync(destFontsDir)) {
  fs.mkdirSync(destFontsDir, { recursive: true });
}

// Copy and modify CSS file
if (fs.existsSync(srcCss)) {
  let cssContent = fs.readFileSync(srcCss, 'utf8');
  // Replace existing font-display definitions with swap, or prepend if missing
  if (cssContent.includes('font-display:')) {
    cssContent = cssContent.replace(/font-display:\s*[^;]+;/g, 'font-display: swap;');
  } else {
    cssContent = cssContent.replace('@font-face {', '@font-face {\n  font-display: swap;');
  }
  fs.writeFileSync(path.join(destCssDir, 'bootstrap-icons.css'), cssContent);
  console.log('Copied and modified bootstrap-icons.css (font-display: swap resolved) to static/css/');
} else {
  console.error('Source bootstrap-icons.css not found!');
}

// Copy Font files
if (fs.existsSync(srcFontsDir)) {
  const files = fs.readdirSync(srcFontsDir);
  files.forEach(file => {
    fs.copyFileSync(path.join(srcFontsDir, file), path.join(destFontsDir, file));
  });
  console.log('Copied font files to static/css/fonts/');
} else {
  console.error('Source fonts directory not found!');
}
