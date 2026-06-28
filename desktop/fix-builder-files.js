/**
 * fix-builder-files.js
 *
 * Electron build sonrasi .py dosyalarini app.asar disina cikarmak icin
 * yardimci script. asarUnpack calismazsa manuel olarak dosyalari kopyalar.
 *
 * Kullanim:
 *   node fix-builder-files.js
 *   npm run fix:asar
 *
 * Ne yapar:
 *   1. python_bridge.py'yi resources/ altina kopyalar (extraResources)
 *   2. .env dosyasini resources/ altina kopyalar
 *   3. web_ui.py varsa kontrol eder
 *   4. asar.unpacked klasorunu kontrol eder
 */

const fs = require('fs');
const path = require('path');

const DIST_DIR = path.join(__dirname, 'dist', 'win-unpacked');
const RESOURCES_DIR = path.join(DIST_DIR, 'resources');
const ASAR_UNPACKED_DIR = path.join(RESOURCES_DIR, 'app.asar.unpacked');
const SRC_DIR = __dirname;

const REQUIRED_FILES = [
    { src: 'python_bridge.py', dest: 'python_bridge.py' },
    { src: path.join('..', '.env'), dest: '.env' },
];

console.log('=== ReYMeN ASAR Fix Builder ===');
console.log(`  Hedef: ${RESOURCES_DIR}`);
console.log('');

// 1. Klasorleri kontrol et
if (!fs.existsSync(DIST_DIR)) {
    console.error('✘ dist/win-unpacked/ bulunamadi!');
    console.log('  Önce npm run build calistirin.');
    process.exit(1);
}

if (!fs.existsSync(RESOURCES_DIR)) {
    console.error('✘ resources/ klasoru bulunamadi!');
    process.exit(1);
}

if (!fs.existsSync(path.join(RESOURCES_DIR, 'app.asar'))) {
    console.error('✘ app.asar bulunamadi!');
    process.exit(1);
}

// 2. asar.unpacked kontrol
if (fs.existsSync(ASAR_UNPACKED_DIR)) {
    const unpackedFiles = fs.readdirSync(ASAR_UNPACKED_DIR);
    console.log(`✓ asar.unpacked mevcut: ${unpackedFiles.length} dosya`);
    unpackedFiles.forEach(f => console.log(`  - ${f}`));
} else {
    console.log('⚠ asar.unpacked yok (asarUnpack calismamis olabilir)');
    console.log('  Manuel kopyalama yapiliyor...');
}

// 3. Dosyalari kopyala
let copied = 0;
let errors = 0;

REQUIRED_FILES.forEach(({ src, dest }) => {
    const srcPath = path.join(SRC_DIR, src);
    const destPath = path.join(RESOURCES_DIR, dest);

    if (!fs.existsSync(srcPath)) {
        console.log(`  ? Kaynak yok: ${srcPath}`);
        errors++;
        return;
    }

    if (fs.existsSync(destPath)) {
        const srcSize = fs.statSync(srcPath).size;
        const destSize = fs.statSync(destPath).size;
        if (srcSize === destSize) {
            console.log(`  ✓ ${dest} zaten guncel (${srcSize} bytes)`);
            return;
        }
    }

    try {
        fs.copyFileSync(srcPath, destPath);
        console.log(`  ✓ ${dest} kopyalandi (${fs.statSync(srcPath).size} bytes)`);
        copied++;
    } catch (e) {
        console.error(`  ✘ ${dest} kopyalanamadi: ${e.message}`);
        errors++;
    }
});

// 4. web_ui.py kontrol
const webUiPath = path.join(RESOURCES_DIR, 'web_ui.py');
if (fs.existsSync(webUiPath)) {
    console.log(`✓ web_ui.py mevcut (${fs.statSync(webUiPath).size} bytes)`);
} else {
    console.log('⚠ web_ui.py resources/ altinda yok! extraResources calismamis.');
    // web_ui.py'yi manuel kopyala
    const srcWebUi = path.join(__dirname, '..', 'web_ui.py');
    if (fs.existsSync(srcWebUi)) {
        try {
            fs.copyFileSync(srcWebUi, webUiPath);
            console.log('  ✓ web_ui.py manuel kopyalandi');
            copied++;
        } catch (e) {
            console.error(`  ✘ web_ui.py kopyalanamadi: ${e.message}`);
            errors++;
        }
    }
}

console.log('');
console.log('=== Ozet ===');
console.log(`  Kopyalanan: ${copied} dosya`);
console.log(`  Hata: ${errors}`);
console.log('');
if (copied > 0 || errors === 0) {
    console.log('✅ ASAR fix tamam. Simdi Electron uygulamasi baslatilabilir.');
} else {
    console.log('❌ Hatalar var. Elle kontrol edin.');
}
