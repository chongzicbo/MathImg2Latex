let imageSavePath = "";
let sourceFormula = "";
const save_directory = "/data/bocheng/data/test/images"
window.onload = function () {
    hideElementsIfEmpty()
};
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
                const imagePath = `${save_directory}/${filename}`;

                const imageBlob = dataURItoBlob(imageData);
                saveBlobAsFile(imageBlob, filename, save_directory);
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
// 这个函数用于更新显示的公式并重新渲染MathJax内容
function updateFormulaDisplay(latex) {
    let formulaResultElement = document.getElementById('formulaResult');

    // 设置并显示新的LaTeX公式
    formulaResultElement.textContent = `$$${latex}$$`;
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, formulaResultElement]);
}

// 在用户对LaTeX源码作出更改时更新和渲染公式
document.getElementById('formulaSource').addEventListener('input', function () {
    updateFormulaDisplay(this.value);
});

// extractFormula函数从服务器获取提取的LaTeX公式，并更新显示
async function extractFormula(model) {
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
        document.getElementById('formulaSource').value = latexFormula; // 将提取的公式设置为文本域的值

        // 更新显示的公式并重新渲染MathJax内容
        updateFormulaDisplay(latexFormula);

        sourceFormula = latexFormula; // 保存原始获取的LaTeX公式
        hideElementsIfEmpty();
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

function saveBlobAsFile(blob, filename, saveDirectory) {
    const reader = new FileReader();
    reader.onloadend = function () {
        const arrayBuffer = reader.result;
        const uint8Array = new Uint8Array(arrayBuffer);
        const file = new File([uint8Array], filename, { type: blob.type });
        const formData = new FormData();
        formData.append('file', file);
        formData.append('directory', saveDirectory);
        fetch('/save_image', {
            method: 'POST',
            body: formData
        });
    };
    reader.readAsArrayBuffer(blob);
}

function hideElementsIfEmpty() {
    const formulaSource = document.getElementById('formulaSource');
    const formulaResult = document.getElementById('formulaResult');
    const saveButton = document.getElementById('saveButton');
    const formulaSourceLabel = document.getElementById("formulaSourceLabel")

    // 检查内容是否为空
    if (formulaSource.innerText.trim() === '' && formulaResult.innerText.trim() === '') {
        formulaSource.style.display = 'none';
        formulaResult.style.display = 'none';
        saveButton.style.display = 'none';
        formulaSourceLabel.style.display = 'none'
    } else {
        formulaSource.style.display = 'block';
        formulaResult.style.display = 'block';
        saveButton.style.display = 'block';
        formulaSourceLabel.style.display = "block"
    }
}