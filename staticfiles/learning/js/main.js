console.log('JavaScript file loaded successfully');

// Make sure openChatbot is defined at the global scope
function openChatbot() {
    console.log('openChatbot function called');
    const modal = new bootstrap.Modal(document.getElementById('chatbotModal'));
    modal.show();
}

// to make sure the function is available globally
window.openChatbot = openChatbot;

// Global Variables
let currentPage = 'home';
let chatHistory = [];
let quizAnswers = {
    q1: 'b',
    q2: 'a', 
    q3: 'a',
    q4: 'a',
    q5: 'a'
};

// Page Navigation
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    currentPage = pageId;
    
    // Show/hide navbar based on page
    const navbar = document.getElementById('navbar');
    if (pageId === 'home') {
        navbar.classList.add('d-none');
    } else {
        navbar.classList.remove('d-none');
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
    
    // Initialize page-specific functionality
    initializePage(pageId);
}

function initializePage(pageId) {
    if (pageId === 'home') {
        // Initialize fade-in animations
        observeElements();
    } else if (pageId === 'quiz') {
        // Initialize quiz functionality
        initializeQuiz();
    }
}

// Animation Observer
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    });

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

// Quiz Functionality
function initializeQuiz() {
    const quizOptions = document.querySelectorAll('.quiz-option');
    quizOptions.forEach(option => {
        option.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            const questionOptions = document.querySelectorAll(`[data-question="${question}"]`);
            
            // Remove selected class from all options in this question
            questionOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Check the radio button
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // Handle form submission
    document.getElementById('quizForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuiz();
    });
}

function submitQuiz() {
    const formData = new FormData(document.getElementById('quizForm'));
    let score = 0;
    let totalQuestions = Object.keys(quizAnswers).length;
    
    // Check answers
    for (let [question, correctAnswer] of Object.entries(quizAnswers)) {
        if (formData.get(question) === correctAnswer) {
            score++;
        }
    }
    
    // Show result
    document.getElementById('quizForm').style.display = 'none';
    document.getElementById('quizResult').style.display = 'block';
    
    // Update score text
    const scoreText = document.getElementById('scoreText');
    const percentage = Math.round((score / totalQuestions) * 100);
    
    if (percentage >= 80) {
        scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Excellent work! 🏆`;
    } else if (percentage >= 60) {
        scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Good job! 👍`;
    } else {
        scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Keep learning! 📚`;
    }
}

function retakeQuiz() {
    document.getElementById('quizForm').style.display = 'block';
    document.getElementById('quizResult').style.display = 'none';
    
    // Reset form
    document.getElementById('quizForm').reset();
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.classList.remove('selected');
    });
}

// Form Handling
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    // Simulate login
    setTimeout(() => {
        alert('Login successful! Welcome to JuaSmart!');
        showPage('dashboard');
    }, 1000);
});

document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    // Simulate registration
    setTimeout(() => {
        alert('Registration successful! Welcome to JuaSmart!');
        showPage('dashboard');
    }, 1000);
});

// Chat input enter key
document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    showPage('home');
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});