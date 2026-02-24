// static/js/upload.js

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const form = document.getElementById('uploadForm');
    const fileInput = form.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('previewContainer');
    const statusMessages = document.getElementById('statusMessages');
    
    // Allow multiple files
    fileInput.setAttribute('multiple', 'multiple');
    
    // Click to browse
    dropzone.addEventListener('click', () => fileInput.click());
    
    // Drag events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('border-accent', 'bg-accent/10');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('border-accent', 'bg-accent/10');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('border-accent', 'bg-accent/10');
        handleFiles(e.dataTransfer.files);
    });
    
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    
    function handleFiles(files) {
        previewContainer.innerHTML = '';
        statusMessages.innerHTML = '';
        Array.from(files).forEach(file => {
            const preview = createPreview(file);
            previewContainer.appendChild(preview);
            uploadFile(file);
        });
    }
    
    function createPreview(file) {
        const div = document.createElement('div');
        div.className = 'relative rounded-xl overflow-hidden aspect-square bg-muted/20';
        
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.className = 'w-full h-full object-cover';
            div.appendChild(img);
        } else if (file.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = URL.createObjectURL(file);
            video.className = 'w-full h-full object-cover';
            video.muted = true;
            div.appendChild(video);
        } else {
            const icon = document.createElement('div');
            icon.className = 'w-full h-full flex-center text-4xl';
            icon.textContent = '📄';
            div.appendChild(icon);
        }
        
        const name = document.createElement('p');
        name.className = 'absolute bottom-0 left-0 right-0 bg-black/50 text-white text-sm p-2 truncate';
        name.textContent = file.name;
        div.appendChild(name);
        
        return div;
    }
    
    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');  // Django CSRF
        formData.append('file', file);
        
        try {
            const response = await fetch('{% url "upload" %}', {
                method: 'POST',
                body: formData,
                headers: { 'x-requested-with': 'XMLHttpRequest' }
            });
            
            const data = await response.json();
            const msg = document.createElement('p');
            msg.textContent = data.success ? `${file.name} uploaded successfully!` : `Error uploading ${file.name}`;
            msg.className = data.success ? 'text-green-400' : 'text-red-400';
            statusMessages.appendChild(msg);
        } catch (error) {
            const msg = document.createElement('p');
            msg.textContent = `Upload failed for ${file.name}: ${error}`;
            msg.className = 'text-red-400';
            statusMessages.appendChild(msg);
        }
    }
});
