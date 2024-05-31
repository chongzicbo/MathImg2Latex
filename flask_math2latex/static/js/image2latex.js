let imageSavePath = "";
let sourceFormula = "";
const imageSaveDirectory = '/data/bocheng/data/test/images';
function generateRandomFileName() {
    // 生成一个随机的36进制字符串
    const randomString = Math.random().toString(36).substring(2);
    // 添加文件扩展名
    return `pasted_image_${randomString}.png`;
}
document.getElementById('pasteBox').addEventListener('paste', function (e) {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') === 0) {
            const blob = items[i].getAsFile();
            const reader = new FileReader();
            reader.onloadend = function () {
                const imageData = reader.result;
                document.getElementById('pasteBox').value = imageData;

                // Save the image data to a file
                const filename = generateRandomFileName();
                const imagePath = `${imageSaveDirectory}/${filename}`;

                const imageBlob = dataURItoBlob(imageData);
                saveBlobAsFile(imageBlob, imagePath);
                imageSavePath = imagePath
                // Display the uploaded image
                const imageUrl = URL.createObjectURL(imageBlob);
                document.getElementById('uploadedImage').src = imageUrl;
                document.getElementById('uploadedImage').style.display = 'block';
            };
            reader.readAsDataURL(blob);
            break;
        }
    }
});
async function extractFormula(model) {
    // Now extract the formula
    if (!imageSavePath) {
        alert('Please paste an image into the text box.');
        return;
    }
    try {
        const response = await fetch(`/extract?model=${model}&image_path=${encodeURIComponent(imageSavePath)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const latexFormula = await response.text();
        document.getElementById('formulaResult').innerHTML = `$$${latexFormula}$$`;
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
        sourceFormula = latexFormula; // 在这里设置sourceFormula
    } catch (error) {
        console.error('Error extracting formula:', error);
    }
}
function saveResult() {
    const formulaElement = document.getElementById('formulaResult');
    let formula = formulaElement.innerText || formulaElement.textContent;

    // 去除LaTeX公式字符串的HTML标签
    formula = formula.replace(/<[^>]*>/g, '').trim();

    if (!formula.trim()) {
        alert("Please paste an image and extract the formula first.");
        return;
    }

    fetch('/save_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            formula: sourceFormula,
            image_path: imageSavePath
        })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Error saving result:', error);
        });
}

function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

function saveBlobAsFile(blob, filename) {
    const reader = new FileReader();
    reader.onloadend = function () {
        const arrayBuffer = reader.result;
        const uint8Array = new Uint8Array(arrayBuffer);
        const file = new File([uint8Array], filename, { type: blob.type });
        const formData = new FormData();
        formData.append('file', file);
        fetch('/save_image', {
            method: 'POST',
            body: formData
        });
    };
    reader.readAsArrayBuffer(blob);
}