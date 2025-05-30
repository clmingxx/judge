// 全局变量声明
let refreshInterval = null;
let modalRefreshInterval = null;
let currentItemName = null;

// 主界面自动刷新控制
function startAutoRefresh() {
    // 每30秒刷新一次主界面内容
    refreshInterval = setInterval(() => {
        if (!currentItemName) {
            window.location.reload();
        } else {
            refreshMainContent();
        }
    }, 30000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// 弹窗自动刷新控制
function startModalRefresh(itemName) {
    // 每5秒刷新一次弹窗内容
    modalRefreshInterval = setInterval(() => {
        refreshModalContent(itemName);
    }, 5000);
}

function stopModalRefresh() {
    if (modalRefreshInterval) {
        clearInterval(modalRefreshInterval);
        modalRefreshInterval = null;
    }
}

// 内容刷新函数
function refreshMainContent() {
    fetch('/display')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html,  'text/html');
            const newContent = doc.querySelector('.container').innerHTML;
            document.querySelector('.container').innerHTML  = newContent;

            // 重新绑定点击事件
            bindItemClickEvents();
        })
        .catch(error => {
            console.error(' 刷新主界面失败:', error);
        });
}

function refreshModalContent(itemName) {
    const modal = document.getElementById('item-details-modal');
    if (modal.style.display  === 'block') {
        fetch(`/display/${encodeURIComponent(itemName)}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('modal-content').innerHTML  = html;
                initAutoScroll();
            })
            .catch(error => {
                console.error(' 刷新弹窗内容失败:', error);
            });
    }
}

// 弹窗控制函数
function loadItemDetails(itemName) {
    currentItemName = itemName;
    window.location.hash  = 'modal';

    const modal = document.getElementById('item-details-modal');
    modal.style.display  = 'block';
    modal.classList.add('show');

    // 更新活动项目样式
    document.querySelectorAll('.item-group').forEach(group  => {
        group.classList.remove('active');
    });
    event.target.closest('.item-group').classList.add('active');

    // 控制刷新逻辑
    stopAutoRefresh();
    stopModalRefresh();
    startModalRefresh(itemName);

    // 加载初始内容
    fetch(`/display/${encodeURIComponent(itemName)}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('modal-content').innerHTML  = html;
            initAutoScroll();
        })
        .catch(error => {
            console.error(' 加载项目详情失败:', error);
            document.getElementById('modal-content').innerHTML  = '<p>加载项目详情失败，请稍后再试。</p>';
        });
}

function closeModal() {
    const modal = document.getElementById('item-details-modal');
    modal.classList.add('hide');

    modal.addEventListener('animationend',  () => {
        modal.classList.remove('show',  'hide');
        modal.style.display  = 'none';

        // 清除弹窗相关状态
        stopModalRefresh();
        document.querySelectorAll('.item-group').forEach(group  => {
            group.classList.remove('active');
        });

        // 恢复主界面刷新
        startAutoRefresh();
        currentItemName = null;
        window.location.hash  = '';
    }, { once: true });
}

// 自动滚动功能
function initAutoScroll() {
    const scoreContainer = document.querySelector('.score-container');
    if (scoreContainer) {
        stopAutoScroll(scoreContainer);
        startAutoScroll(scoreContainer);
    }
}

function startAutoScroll(container) {
    const scrollDuration = 10000;
    let scrollInterval;

    function scrollContent() {
        const maxHeight = container.scrollHeight  - container.clientHeight;
        const currentScroll = container.scrollTop;

        if (maxHeight <= 0) {
            stopAutoScroll(container);
            return;
        }

        const scrollStep = maxHeight / (scrollDuration / 10);

        if (currentScroll >= maxHeight) {
            container.scrollTop  = 0;
        } else {
            container.scrollTop  += scrollStep;
            if (container.scrollTop  === currentScroll) {
                container.scrollTop  = currentScroll + 1;
            }
        }
    }

    if (container.scrollInterval)  {
        clearInterval(container.scrollInterval);
    }

    scrollInterval = setInterval(scrollContent, 10);
    container.scrollInterval  = scrollInterval;

    container.addEventListener('mouseenter',  () => {
        clearInterval(scrollInterval);
    });

    container.addEventListener('mouseleave',  () => {
        scrollInterval = setInterval(scrollContent, 10);
        container.scrollInterval  = scrollInterval;
    });
}

function stopAutoScroll(container) {
    if (container.scrollInterval)  {
        clearInterval(container.scrollInterval);
        container.scrollInterval  = null;
    }
}

// 事件绑定函数
function bindItemClickEvents() {
    document.querySelectorAll('.item-group  .score').forEach(link => {
        link.onclick  = function(e) {
            e.preventDefault();
            const itemName = this.closest('.item-group').querySelector('h3').textContent;
            loadItemDetails(itemName);
        };
    });
}

// 页面初始化
document.addEventListener('DOMContentLoaded',  function() {
    // 开始主界面自动刷新
    startAutoRefresh();

    // 绑定所有项目点击事件
    bindItemClickEvents();

    // 检查URL哈希，恢复弹窗状态
    if (window.location.hash  === '#modal') {
        const activeItem = document.querySelector('.item-group.active  h3');
        if (activeItem) {
            loadItemDetails(activeItem.textContent);
        }
    }
});

// 将关键函数暴露到全局作用域
window.loadItemDetails  = loadItemDetails;
window.closeModal  = closeModal;