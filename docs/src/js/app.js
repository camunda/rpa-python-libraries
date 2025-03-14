document.addEventListener('DOMContentLoaded', function() {
    const pages = [
        'Archive.html',
        'Browser.Selenium.html',
        'Calendar.html',
        'Camunda.html',
        'Desktop.html',
        'Desktop.OperatingSystem.html',
        'Excel.Application.html',
        'Excel.Files.html',
        'FileSystem.html',
        'FTP.html',
        'HTTP.html',
        'Images.html',
        'JavaAccessBridge.html',
        'MFA.html',
        'MSGraph.html',
        'Outlook.Application.html',
        'PDF.html',
        'SAP.html',
        'Tables.html',
        'Tasks.html',
        'Windows.html',
        'Word.Application.html',
    ];

    const navList = document.getElementById('nav-list');
    const contentFrame = document.getElementById('content-frame');

    pages.forEach(page => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${page}`;
        a.textContent = page.replace('.html', '');
        a.addEventListener('click', function(event) {
            event.preventDefault();
            document.querySelectorAll('.sidebar a').forEach(link => link.classList.remove('active'));
            a.classList.add('active');
            contentFrame.src = `pages/${page}`;
        });
        li.appendChild(a);
        navList.appendChild(li);
    });

    // Set the default active link
    document.querySelector('.sidebar a').classList.add('active');
});
