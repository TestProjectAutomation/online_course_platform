// =====================
// إصلاحات JavaScript لـ RTL
// =====================

document.addEventListener('DOMContentLoaded', function() {

    // إصلاح أيقونات الأسهم في القوائم
    fixSidebarIcons();

    // إصلاح اتجاه أزرار التنقل
    fixPagination();

    // إصلاح اتجاه القوائم المنسدلة
    fixDropdowns();

    // إضافة دعم للغة العربية في محرر النصوص
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function(ev) {
            ev.editor.lang.direction = 'rtl';
            ev.editor.lang.code = 'ar';
        });
    }

    // إصلاح أيقونات التقويم
    fixCalendarIcons();

    // مراقبة تغييرات DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                fixSidebarIcons();
                fixPagination();
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// إصلاح أيقونات الشريط الجانبي
function fixSidebarIcons() {
    document.querySelectorAll('.nav-item.has-treeview > .nav-link').forEach(link => {
        if (!link.querySelector('.fa-chevron-left, .fa-chevron-right')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-chevron-left';
            link.appendChild(icon);
        }
    });
}

// إصلاح أزرار التنقل
function fixPagination() {
    document.querySelectorAll('.pagination .page-item:first-child .page-link').forEach(btn => {
        if (btn.innerHTML.includes('chevron-right')) {
            btn.innerHTML = btn.innerHTML.replace('chevron-right', 'chevron-left');
        }
    });

    document.querySelectorAll('.pagination .page-item:last-child .page-link').forEach(btn => {
        if (btn.innerHTML.includes('chevron-left')) {
            btn.innerHTML = btn.innerHTML.replace('chevron-left', 'chevron-right');
        }
    });
}

// إصلاح القوائم المنسدلة
function fixDropdowns() {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu.classList.contains('dropdown-menu-right')) {
            menu.classList.remove('dropdown-menu-right');
            menu.classList.add('dropdown-menu-left');
        }
    });
}

// إصلاح أيقونات التقويم
function fixCalendarIcons() {
    document.querySelectorAll('.datetimeshortcuts a').forEach(link => {
        if (link.innerHTML.includes('calendar') || link.innerHTML.includes('clock')) {
            link.style.marginLeft = '0';
            link.style.marginRight = '0.5rem';
        }
    });
}

// دالة لتبديل اتجاه الصفحة
function toggleRTL() {
    const html = document.documentElement;
    if (html.dir === 'rtl') {
        html.dir = 'ltr';
        html.style.direction = 'ltr';
    } else {
        html.dir = 'rtl';
        html.style.direction = 'rtl';
    }
}

// دالة لتحميل الإحصائيات (اختياري)
function loadDashboardStats() {
    fetch('/ajax/dashboard-stats/')
        .then(response => response.json())
        .then(data => {
            // تحديث الإحصائيات في لوحة التحكم
            console.log('Dashboard stats:', data);
        })
        .catch(error => console.error('Error loading stats:', error));
}

// تنفيذ بعد تحميل الصفحة بالكامل
window.addEventListener('load', function() {
    // تأخير بسيط للتأكد من تحميل كل العناصر
    setTimeout(fixSidebarIcons, 100);
    setTimeout(fixPagination, 100);
    setTimeout(fixDropdowns, 100);
    setTimeout(fixCalendarIcons, 100);
});