// ================================================
// Doctor AI - Custom JavaScript
// ================================================

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTooltips();
    initializeModals();
    initializeDatePickers();
    initializeFormValidation();
    initializeAutoLogout();
});

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap Modals
function initializeModals() {
    var modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    var modalList = modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

// Initialize Date Pickers
function initializeDatePickers() {
    // Set minimum date for date inputs to today
    var today = new Date().toISOString().split('T')[0];
    var dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(function(input) {
        if (!input.hasAttribute('min')) {
            input.setAttribute('min', today);
        }
    });
}

// Initialize Form Validation
function initializeFormValidation() {
    var forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Auto Logout Timer (30 minutes of inactivity)
function initializeAutoLogout() {
    var inactivityTime = function () {
        var time;
        window.onload = resetTimer;
        document.onmousemove = resetTimer;
        document.onkeypress = resetTimer;
        document.ontouchstart = resetTimer;
        document.onclick = resetTimer;
        document.onscroll = resetTimer;
        
        function logout() {
            // Redirect to logout page
            window.location.href = '/auth/logout';
        }
        
        function resetTimer() {
            clearTimeout(time);
            time = setTimeout(logout, 1800000); // 30 minutes
        }
    };
    
    inactivityTime();
}

// Confirm Action Helper
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// Search Filter Helper
function filterTable(tableId, searchInputId) {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById(searchInputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

// Loading Spinner Helper
function showLoading(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        element.disabled = true;
    }
}

function hideLoading(elementId, originalText) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// AJAX Request Helper
function makeAjaxRequest(url, method, data, successCallback, errorCallback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            if (successCallback) {
                successCallback(JSON.parse(xhr.responseText));
            }
        } else {
            if (errorCallback) {
                errorCallback(xhr.status, xhr.statusText);
            }
        }
    };
    
    xhr.onerror = function() {
        if (errorCallback) {
            errorCallback(xhr.status, xhr.statusText);
        }
    };
    
    if (data) {
        xhr.send(JSON.stringify(data));
    } else {
        xhr.send();
    }
}

// Real-time Search Helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Password Strength Checker
function checkPasswordStrength(password) {
    var strength = 0;
    
    if (password.length >= 8) {
        strength += 1;
    }
    
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
        strength += 1;
    }
    
    if (password.match(/\d/)) {
        strength += 1;
    }
    
    if (password.match(/[^a-zA-Z\d]/)) {
        strength += 1;
    }
    
    return strength;
}

// Display Password Strength
function displayPasswordStrength(password, elementId) {
    var strength = checkPasswordStrength(password);
    var element = document.getElementById(elementId);
    
    if (element) {
        var messages = ['Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'];
        var colors = ['#dc3545', '#dc3545', '#ffc107', '#28a745', '#28a745'];
        
        element.textContent = messages[strength];
        element.style.color = colors[strength];
    }
}

// Format Date Helper
function formatDate(dateString) {
    var date = new Date(dateString);
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Format Time Helper
function formatTime(timeString) {
    var time = new Date(timeString);
    var options = { hour: '2-digit', minute: '2-digit' };
    return time.toLocaleTimeString('en-US', options);
}

// Get URL Parameters
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Set URL Parameter
function setUrlParameter(name, value) {
    var url = new URL(window.location.href);
    url.searchParams.set(name, value);
    window.history.replaceState({}, '', url);
}

// Remove URL Parameter
function removeUrlParameter(name) {
    var url = new URL(window.location.href);
    url.searchParams.delete(name);
    window.history.replaceState({}, '', url);
}

// Copy to Clipboard Helper
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard!');
    }, function(err) {
        console.error('Failed to copy: ', err);
    });
}

// Local Storage Helper
function saveToLocalStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function getFromLocalStorage(key) {
    var item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
}

function removeFromLocalStorage(key) {
    localStorage.removeItem(key);
}

// Session Storage Helper
function saveToSessionStorage(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

function getFromSessionStorage(key) {
    var item = sessionStorage.getItem(key);
    return item ? JSON.parse(item) : null;
}

function removeFromSessionStorage(key) {
    sessionStorage.removeItem(key);
}

// Alert Dismissal Timer
function autoDismissAlert(alertElement, delay) {
    setTimeout(function() {
        if (alertElement) {
            var bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, delay || 5000);
}

// Smooth Scroll Helper
function smoothScrollTo(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Toggle Password Visibility
function togglePasswordVisibility(inputId, iconId) {
    var input = document.getElementById(inputId);
    var icon = document.getElementById(iconId);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Validate Email Format
function isValidEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate Phone Number Format
function isValidPhone(phone) {
    var re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone);
}

// Get Current User Info
function getCurrentUserInfo() {
    var userInfo = getFromSessionStorage('userInfo');
    return userInfo || null;
}

// Check User Role
function hasRole(role) {
    var userInfo = getCurrentUserInfo();
    return userInfo && userInfo.role === role;
}

// Redirect Based on Role
function redirectBasedOnRole() {
    var userInfo = getCurrentUserInfo();
    if (userInfo) {
        switch(userInfo.role) {
            case 'patient':
                window.location.href = '/patient/dashboard';
                break;
            case 'doctor':
                window.location.href = '/doctor/dashboard';
                break;
            case 'admin':
                window.location.href = '/admin/dashboard';
                break;
            default:
                window.location.href = '/';
        }
    }
}

// Show Notification
function showNotification(message, type) {
    var notification = document.createElement('div');
    notification.className = 'alert alert-' + type + ' alert-dismissible fade show';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        autoDismissAlert(notification);
    }
}

// Initialize Everything When DOM is Ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        autoDismissAlert(alert);
    });
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            var href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                smoothScrollTo(href.substring(1));
            }
        });
    });
});
