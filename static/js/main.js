// main.js — students will add JavaScript here as features are built

// Video Modal Functionality
(function() {
    const modal = document.getElementById('video-modal');
    const openBtn = document.getElementById('how-it-works-btn');
    const closeBtn = document.getElementById('modal-close-btn');
    const videoFrame = document.getElementById('video-frame');

    // YouTube video URL (placeholder - replace with actual video ID)
    const videoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1';

    // Open modal
    openBtn.addEventListener('click', function(e) {
        e.preventDefault();
        videoFrame.src = videoUrl;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    // Close modal function
    function closeModal() {
        modal.classList.remove('active');
        videoFrame.src = '';
        document.body.style.overflow = '';
    }

    // Close on close button click
    closeBtn.addEventListener('click', closeModal);

    // Close on overlay click (outside modal)
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
})();
