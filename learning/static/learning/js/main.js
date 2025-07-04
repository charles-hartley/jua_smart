console.log('JavaScript file loaded successfully');

// Make sure openChatbot is defined at the global scope
function openChatbot() {
    console.log('openChatbot function called');
    const modal = document.getElementById('chatbotModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
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
    // Hide all pages - but only if they exist
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page - but only if it exists
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = pageId;
    }
    
    // Show/hide navbar based on page - but only if navbar exists
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (pageId === 'home') {
            navbar.classList.add('d-none');
        } else {
            navbar.classList.remove('d-none');
        }
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

    // Handle form submission - but only if form exists
    const quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitQuiz();
        });
    }
}

function submitQuiz() {
    const quizForm = document.getElementById('quizForm');
    const quizResult = document.getElementById('quizResult');
    
    if (!quizForm || !quizResult) return;
    
    const formData = new FormData(quizForm);
    let score = 0;
    let totalQuestions = Object.keys(quizAnswers).length;
    
    // Check answers
    for (let [question, correctAnswer] of Object.entries(quizAnswers)) {
        if (formData.get(question) === correctAnswer) {
            score++;
        }
    }
    
    // Show result
    quizForm.style.display = 'none';
    quizResult.style.display = 'block';
    
    // Update score text - but only if element exists
    const scoreText = document.getElementById('scoreText');
    if (scoreText) {
        const percentage = Math.round((score / totalQuestions) * 100);
        
        if (percentage >= 80) {
            scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Excellent work! 🏆`;
        } else if (percentage >= 60) {
            scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Good job! 👍`;
        } else {
            scoreText.innerHTML = `You scored ${score}/${totalQuestions} (${percentage}%) - Keep learning! 📚`;
        }
    }
}

function retakeQuiz() {
    const quizForm = document.getElementById('quizForm');
    const quizResult = document.getElementById('quizResult');
    
    if (!quizForm || !quizResult) return;
    
    quizForm.style.display = 'block';
    quizResult.style.display = 'none';
    
    // Reset form
    quizForm.reset();
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.classList.remove('selected');
    });
}

// Form Handling - with proper DOM checks
function initializeForms() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Simulate login
            setTimeout(() => {
                alert('Login successful! Welcome to JuaSmart!');
                showPage('dashboard');
            }, 1000);
        });
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            // Let Django handle form submission normally
        });
    }

    // Chat input enter key
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Check if we're on a single-page app or a separate page
    const homePageExists = document.getElementById('home');
    
    if (homePageExists) {
        // We're on the main single-page app
        showPage('home');
    } else {
        // We're on a separate page (like dashboard.html)
        console.log('On separate page - skipping SPA initialization');
    }
    
    // Initialize forms regardless of page type
    initializeForms();
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
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
});

// Function to send chat messages (if needed)
function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    const message = chatInput.value.trim();
    if (message === '') return;
    
    // Add message to chat history
    chatHistory.push({
        user: 'You',
        message: message,
        timestamp: new Date()
    });
    
    // Clear input
    chatInput.value = '';
    
    // Here you would typically send the message to your backend
    console.log('Message sent:', message);
}