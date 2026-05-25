
document.addEventListener('DOMContentLoaded', () => {
    // --- 商品データ ---
    const products = {
        fashion: [
            { id: 'fa1', name: 'Tシャツ', price: 2500, image: 'images/Tシャツ.png' },
            { id: 'fa2', name: 'パーカー', price: 5800, image: 'images/パーカー.png' },
            { id: 'fa3', name: 'ジーンズ', price: 8900, image: 'images/ジーンズ.png' },
            { id: 'fa4', name: 'スカート', price: 4500, image: 'images/スカート.png' },
            { id: 'fa5', name: 'スニーカー', price: 12000, image: 'images/スニーカー.png' },
            { id: 'fa6', name: '帽子', price: 3200, image: 'images/帽子.png' },
            { id: 'fa7', name: 'リュックサック', price: 7500, image: 'images/リュックサック.png' },
            { id: 'fa8', name: '靴下', price: 1200, image: 'images/靴下.png' }
        ],
        electronics: [
            { id: 'el1', name: 'カメラ', price: 65000, image: 'images/カメラ.png' },
            { id: 'el2', name: 'スマートフォン', price: 98000, image: 'images/スマートフォン.png' },
            { id: 'el3', name: 'パソコン', price: 125000, image: 'images/パソコン.png' },
            { id: 'el4', name: 'ヘッドホン', price: 28000, image: 'images/ヘッドホン.png' },
            { id: 'el5', name: 'スピーカー', price: 15000, image: 'images/スピーカー.png' },
            { id: 'el6', name: '時計', price: 35000, image: 'images/時計.png' },
            { id: 'el7', name: 'テレビ', price: 80000, image: 'images/テレビ.png' },
            { id: 'el8', name: 'タブレット', price: 45000, image: 'images/タブレット.png' }
        ],
        furniture: [
            { id: 'fu1', name: 'イス', price: 8500, image: 'images/イス.png' },
            { id: 'fu2', name: '机', price: 22000, image: 'images/机.png' },
            { id: 'fu3', name: 'ソファー', price: 45000, image: 'images/ソファー.png' },
            { id: 'fu4', name: 'ベッド', price: 60000, image: 'images/ベッド.png' },
            { id: 'fu5', name: '棚', price: 12000, image: 'images/棚.png' },
            { id: 'fu6', name: 'カーテン', price: 5500, image: 'images/カーテン.png' },
            { id: 'fu7', name: '鏡', price: 4800, image: 'images/鏡.png' },
            { id: 'fu8', name: 'フロアライト', price: 9800, image: 'images/フロアライト.png' }
        ],
        food_drink: [
            { id: 'fd1', name: 'りんご', price: 200, image: 'images/りんご.png' },
            { id: 'fd2', name: 'ミネラルウォーター', price: 120, image: 'images/ミネラルウォーター.png' },
            { id: 'fd3', name: 'コーヒー', price: 450, image: 'images/コーヒー.png' },
            { id: 'fd4', name: 'クロワッサン', price: 180, image: 'images/クロワッサン.png' },
            { id: 'fd5', name: 'パスタ', price: 300, image: 'images/パスタ.png' },
            { id: 'fd6', name: 'チョコレート', price: 250, image: 'images/チョコレート.png' },
            { id: 'fd7', name: 'クッキー', price: 350, image: 'images/クッキー.png' },
            { id: 'fd8', name: 'イチゴジャム', price: 480, image: 'images/イチゴジャム.png' }
        ]
    };

    const tutorialTrials = [
        { taskHTML: '<strong>Tシャツ</strong>と<strong>スマートフォン</strong>をカートに入れてください', loader: 'bouncing-dots', time: 2500 },
        { taskHTML: '<strong>カメラ</strong>と<strong>イス</strong>をカートに入れてください', loader: 'bouncing-dots', time: 2500 },
        { taskHTML: '<p class="tutorial-descriptor" style="font-size: 1.2rem; color: #555;">次に、読み込み時間が短い例を体験していただきます。</p><strong>イス</strong>と<strong>りんご</strong>をカートに入れてください', loader: 'bouncing-dots', time: 1000 }, // 短い例
        { taskHTML: '<p class="tutorial-descriptor" style="font-size: 1.2rem; color: #555;">最後に、読み込み時間が長い例を体験していただきます。</p><strong>コーヒー</strong>と<strong>パーカー</strong>をカートに入れてください', loader: 'bouncing-dots', time: 6000 },       // 長い例
    ];

    // --- 制約付きシャッフル関数 ---
    function createConstrainedShuffle(trials) {
        let attempts = 0;
        while (attempts < 100) { // 無限ループを避けるための安全装置
            let shuffled = [];
            let pool = [...trials];

            while (pool.length > 0) {
                const last = shuffled[shuffled.length - 1];
                const secondLast = shuffled[shuffled.length - 2];

                const candidates = pool.filter(candidate => {
                    // ルール1: 同じUIは2回連続しない
                    if (last && candidate.loader === last.loader) {
                        return false;
                    }
                    // ルール2: 同じ時間は3回連続しない
                    if (last && secondLast && candidate.time === last.time && last.time === secondLast.time) {
                        return false;
                    }
                    return true;
                });

                if (candidates.length === 0) {
                    // 行き止まり。この試行を中断して再試行
                    break;
                }

                const nextIndex = Math.floor(Math.random() * candidates.length);
                const nextTrial = candidates[nextIndex];
                
                shuffled.push(nextTrial);
                
                const originalIndexInPool = pool.findIndex(t => t === nextTrial);
                pool.splice(originalIndexInPool, 1);
            }

            if (shuffled.length === trials.length) {
                // 成功
                console.log(`シャッフル成功 (${attempts + 1}回目)`);
                return shuffled;
            }

            attempts++;
        }

        // 100回試行しても失敗した場合、警告を出して元の順序を返す
        console.warn("有効なシャッフルを作成できませんでした。元の順序を使用します。");
        return trials;
    }

    // --- タスクの文章プール ---
    const taskPool = [
        "<strong>パーカー</strong>と<strong>パソコン</strong>をカートに入れてください",
        "<strong>スマートフォン</strong>と<strong>ソファー</strong>をカートに入れてください",
        "<strong>りんご</strong>と<strong>靴下</strong>をカートに入れてください",
        "<strong>リュックサック</strong>と<strong>時計</strong>をカートに入れてください",
        "<strong>机</strong>と<strong>チョコレート</strong>をカートに入れてください",
        "<strong>パソコン</strong>と<strong>スカート</strong>をカートに入れてください",
        "<strong>チョコレート</strong>と<strong>テレビ</strong>をカートに入れてください",
        "<strong>ソファー</strong>と<strong>クロワッサン</strong>をカートに入れてください",
        "<strong>靴下</strong>と<strong>棚</strong>をカートに入れてください",
        "<strong>時計</strong>と<strong>りんご</strong>をカートに入れてください",
        "<strong>棚</strong>と<strong>ヘッドホン</strong>をカートに入れてください",
        "<strong>クロワッサン</strong>と<strong>スニーカー</strong>をカートに入れてください",
        "<strong>テレビ</strong>と<strong>鏡</strong>をカートに入れてください",
        "<strong>鏡</strong>と<strong>パスタ</strong>をカートに入れてください",
        "<strong>パスタ</strong>と<strong>スマートフォン</strong>をカートに入れてください",
        "<strong>スニーカー</strong>と<strong>ベッド</strong>をカートに入れてください",
        "<strong>カメラ</strong>と<strong>帽子</strong>をカートに入れてください",
        "<strong>りんご</strong>と<strong>フロアライト</strong>をカートに入れてください",
        "<strong>チョコレート</strong>と<strong>ジーンズ</strong>をカートに入れてください",
        "<strong>ジーンズ</strong>と<strong>スピーカー</strong>をカートに入れてください",
        "<strong>フロアライト</strong>と<strong>コーヒー</strong>をカートに入れてください"
    ];

    // --- 実験条件（UIと時間）のプール ---
    const conditionPool = [
        { id: 1, loader: "bar-color", time: 5000 },
        { id: 2, loader: "bar", time: 5000 },
        { id: 3, loader: "none", time: 1500 },
        { id: 4, loader: "spinner", time: 3000 },
        { id: 5, loader: "none", time: 3000 },
        { id: 6, loader: "skeleton-color", time: 5000 },
        { id: 7, loader: "spinner", time: 1500 },
        { id: 8, loader: "bar-color", time: 1500 },
        { id: 9, loader: "none", time: 5000 },
        { id: 10, loader: "bar", time: 3000 },
        { id: 11, loader: "bar", time: 1500 },
        { id: 12, loader: "skeleton", time: 5000 },
        { id: 13, loader: "spinner-color", time: 3000 },
        { id: 14, loader: "skeleton-color", time: 1500 },
        { id: 15, loader: "spinner", time: 5000 },
        { id: 16, loader: "skeleton-color", time: 3000 },
        { id: 17, loader: "skeleton", time: 1500 },
        { id: 18, loader: "spinner-color", time: 5000 },
        { id: 19, loader: "spinner-color", time: 1500 },
        { id: 20, loader: "bar-color", time: 3000 },
        { id: 21, loader: "skeleton", time: 3000 }
    ];

    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function createPairedTrials(tasks, conditions) {
        const shuffledTasks = shuffleArray([...tasks]);
        const shuffledConditions = shuffleArray([...conditions]);
        
        // タスク数と条件数が一致していることを前提とする
        return shuffledTasks.map((task, index) => ({
            taskHTML: task,
            loader: shuffledConditions[index].loader,
            time: shuffledConditions[index].time,
            originalTrialNumber: shuffledConditions[index].id
        }));
    }

    // ランダムにペアリングされた実験トライアルを作成
    const trialsToShuffle = createPairedTrials(taskPool, conditionPool);
    
    // シャッフル（制約付き）された実験トライアル
    const experimentTrials = createConstrainedShuffle(trialsToShuffle);

    // --- GoogleフォームのURL (削除) ---

    // --- DOM要素の取得 ---
    const startScreen = document.getElementById('start-screen');
    const tutorialStartScreen = document.getElementById('tutorial-start-screen');
    const tutorialCompleteScreen = document.getElementById('tutorial-complete-screen');
    const taskScreen = document.getElementById('task-screen');
    const ecSiteScreen = document.getElementById('ec-site-screen');
    const surveyScreen = document.getElementById('survey-screen');
    const experimentCompleteScreen = document.getElementById('experiment-complete-screen');
    const taskDescription = document.getElementById('task-description');
    
    const startExperimentBtn = document.getElementById('start-experiment-btn');
    const enterDebugModeBtn = document.getElementById('enter-debug-mode-btn');
    const startTutorialBtn = document.getElementById('start-tutorial-btn');
    const startMainExperimentBtn = document.getElementById('start-main-experiment-btn');
    const startTaskBtn = document.getElementById('start-task-btn');
    const productListContainer = document.getElementById('product-list');
    const categoryNav = document.getElementById('category-nav');
    const loadingOverlay = document.querySelector('.loading-overlay');
    const toastNotification = document.getElementById('toast-notification');
    const completeTaskBtn = document.getElementById('complete-task-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');
    const surveyTaskNumber = document.getElementById('survey-task-number');
    const cartCount = document.getElementById('cart-count');
    const cartSidebarBody = document.getElementById('cart-sidebar-body');

    // 新しいDOM要素
    const taskSurveyForm = document.getElementById('task-survey-form');
    const perceivedTimeInput = document.getElementById('perceived-time'); // Slider input
    const submitSurveyBtn = document.getElementById('submit-survey-btn');

    // --- URLパラメータの取得 ---
    const urlParams = new URLSearchParams(window.location.search);

    // --- デバッグモード ---
    let isDebugMode = urlParams.get('debug') === 'true';

    // デバッグモードが有効な場合、隠しボタンを表示する
    if (isDebugMode) {
        const debugBtn = document.getElementById('enter-debug-mode-btn');
        const backBtn = document.getElementById('back-to-loader-selection-btn');
        if (debugBtn) debugBtn.style.display = 'block';
        if (backBtn) backBtn.style.display = 'block';
    }

    // --- 計測用変数 ---
    let rageClickCount = 0;
    const lastClicks = [];
    const RAGE_CLICK_THRESHOLD_TIME = 500;
    const RAGE_CLICK_THRESHOLD_COUNT = 3;
    let totalMouseDistance = 0;
    let lastMouseX = 0;
    let lastMouseY = 0;
    let isMeasuringMouseDistance = false;
    let taskStartTime = 0;
    let accumulatedLoadingTime = 0;
    const taskTimings = [];
    let taskClickData = []; // For optimal distance calculation

    // --- ヘルパー関数 ---
    function getElementCenter(element) {
        if (!element) return null;
        const rect = element.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2 + window.scrollX,
            y: rect.top + rect.height / 2 + window.scrollY
        };
    }

    function calculateDistance(pos1, pos2) {
        if (!pos1 || !pos2) return 0;
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // --- 状態管理 ---
    let isTutorial = true;
    let tutorialTrialIndex = 0;
    let currentPatternIndex = 0;
    let selectedLoader = 'spinner';
    let loadingTimeMs = 2000;
    let currentCategory = 'home';
    let cartItems = [];
    let cartItemIdCounter = 0;
    let homeVersion = 1;

    // --- 関数定義 ---
    function showScreen(screenToShow) {
        [startScreen, tutorialStartScreen, tutorialCompleteScreen, taskScreen, ecSiteScreen, surveyScreen, experimentCompleteScreen].forEach(screen => {
            if(screen) screen.classList.add('hidden');
        });
        if(screenToShow) screenToShow.classList.remove('hidden');
    }

    function startTutorialTrial(trialIndex) {
        const currentTrial = tutorialTrials[trialIndex];
        selectedLoader = currentTrial.loader;
        loadingTimeMs = currentTrial.time;
        taskDescription.innerHTML = currentTrial.taskHTML;
        showScreen(taskScreen);
    }

    function startTrial(patternIndex) {
        const currentTrial = experimentTrials[patternIndex];
        selectedLoader = currentTrial.loader;
        loadingTimeMs = currentTrial.time;
        taskDescription.innerHTML = currentTrial.taskHTML;
        showScreen(taskScreen);
    }

    function renderCart() {
        cartCount.textContent = cartItems.length;
        cartSidebarBody.innerHTML = '';
        if (cartItems.length === 0) {
            cartSidebarBody.innerHTML = '<p>カートは空です</p>';
        } else {
            const ul = document.createElement('ul');
            cartItems.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span>${item.name} (¥${item.price})</span>
                    <button class="delete-cart-item-btn" data-cart-id="${item.cartId}">&times;</button>
                `;
                ul.appendChild(li);
            });
            cartSidebarBody.appendChild(ul);
        }
    }

    function renderHome() {
        productListContainer.style.display = 'block';
        productListContainer.innerHTML = `
            <div class="hero-section">
                <div class="hero-content">
                    <h1><span style="white-space: nowrap;">理想のライフスタイルを、</span><br>ここから。</h1>
                    <p>最新のガジェットからトレンドのファッションまで、幅広く取り揃えています。</p>
                    <button class="hero-cta-btn" onclick="document.querySelector('[data-category=fashion]').click()">商品を見る</button>
                </div>
            </div>

            <div class="home-section">
                <h2>カテゴリーから探す</h2>
                <div class="category-grid">
                    <div class="category-card" data-category="fashion">
                        <img src="images/Tシャツ.png" alt="ファッション">
                        <span>ファッション</span>
                    </div>
                    <div class="category-card" data-category="electronics">
                        <img src="images/カメラ.png" alt="家電・ガジェット">
                        <span>家電・ガジェット</span>
                    </div>
                    <div class="category-card" data-category="furniture">
                        <img src="images/イス.png" alt="家具・インテリア">
                        <span>家具・インテリア</span>
                    </div>
                    <div class="category-card" data-category="food_drink">
                        <img src="images/りんご.png" alt="食べ物・飲み物">
                        <span>食べ物・飲み物</span>
                    </div>
                </div>
            </div>

            <div class="home-section home-search-container">
                <h2>商品を検索</h2>
                <div class="search-bar">
                    <input type="search" placeholder="キーワードを入力...">
                    <button type="button">検索</button>
                </div>
            </div>
            <button id="switch-home-layout-btn">別のホーム画面</button>
        `;
    }

    function renderHome2() {
        productListContainer.style.display = 'block';
        const featuredProducts = [...products.electronics.slice(0, 2), ...products.fashion.slice(0, 2)];
        productListContainer.innerHTML = `
            <div class="hero-section-2">
                <div class="hero-content-2">
                    <h1>お気に入りの一品、見つけよう。</h1>
                    <p>人気のガジェットや、季節の新作アイテムはいかがですか？</p>
                    <div class="search-bar-2">
                        <input type="search" placeholder="例: スマートフォン, スニーカー">
                        <button type="button">検索</button>
                    </div>
                </div>
                <div class="hero-image-2">
                    <img src="images/スマートフォン.png" alt="Hero Image">
                </div>
            </div>

            <div class="home-section">
                <h2>おすすめ商品</h2>
                <div class="featured-products-grid">
                    ${featuredProducts.map(product => `
                        <div class="product-card">
                            <img src="${product.image}" alt="${product.name}">
                            <div class="product-card-content">
                                <h3>${product.name}</h3>
                                <p class="price">¥${product.price.toLocaleString()}</p>
                            </div>
                            <button class="add-to-cart-btn" data-product-id="${product.id}">カートに入れる</button>
                        </div>
                    `).join('')}
                </div>
            </div>
            <button id="switch-home-layout-btn">別のホーム画面</button>
        `;
    }

    function renderProducts(category) {
        productListContainer.style.display = 'grid';
        const productData = products[category];
        if (!productData) {
            productListContainer.innerHTML = '<p>このカテゴリーの商品は現在ありません。</p>';
            return;
        }
        const categoryTitle = categoryNav.querySelector(`[data-category="${category}"]`).textContent;
        productListContainer.innerHTML = `<h2>${categoryTitle}</h2>` + productData.map(product => `
            <div class="product-card">
                <img src="${product.image}" alt="${product.name}">
                <div class="product-card-content">
                    <h3>${product.name}</h3>
                    <p class="price">¥${product.price.toLocaleString()}</p>
                </div>
                <a href="#" class="add-to-cart-btn" data-product-id="${product.id}" role="button">カートに入れる</a>
            </div>
        `).join('');
    }

    function getLoaderType() { return selectedLoader; }

    function showLoading() {
        const loaderType = getLoaderType();
        loadingOverlay.innerHTML = '';
        if (loaderType.startsWith('bar')) {
            loadingOverlay.innerHTML = '<div class="progress-bar-container"><div class="progress-bar"></div></div>';
            const progressBar = loadingOverlay.querySelector('.progress-bar');
            if (progressBar) {
                if (loaderType === 'bar-color') progressBar.classList.add('color');
                progressBar.style.transitionDuration = `${loadingTimeMs}ms`;
                setTimeout(() => { progressBar.style.width = '100%'; }, 10);
            }
        } else if (loaderType.startsWith('spinner')) {
            loadingOverlay.innerHTML = '<div class="spinner"></div>';
            const spinner = loadingOverlay.querySelector('.spinner');
            if (spinner && loaderType === 'spinner-color') spinner.classList.add('color');
        } else if (loaderType.startsWith('bouncing-dots')) {
            loadingOverlay.innerHTML = '<div class="bouncing-dots"><div></div><div></div><div></div></div>';
            const dots = loadingOverlay.querySelector('.bouncing-dots');
            if (dots && loaderType === 'bouncing-dots-color') dots.classList.add('color');
        }
        loadingOverlay.style.display = 'flex';
    }

    function hideLoading() { loadingOverlay.style.display = 'none'; }

    function showToast(message) {
        toastNotification.textContent = message;
        toastNotification.classList.add('show');
        setTimeout(() => { toastNotification.classList.remove('show'); }, 3000);
    }

    document.addEventListener('mousemove', (e) => {
        if (isMeasuringMouseDistance) {
            if (lastMouseX !== 0 && lastMouseY !== 0) {
                const dx = e.pageX - lastMouseX;
                const dy = e.pageY - lastMouseY;
                totalMouseDistance += Math.sqrt(dx * dx + dy * dy);
            }
            lastMouseX = e.pageX;
            lastMouseY = e.pageY;
        }
    });

    // --- イベントリスナー ---
    function setupDebugUI() {
        const headerRight = document.querySelector('.header-right');
        if (!headerRight || document.getElementById('debug-controls')) return;

        const debugControls = document.createElement('div');
        debugControls.id = 'debug-controls';
        debugControls.style.display = 'flex';
        debugControls.style.gap = '10px';
        debugControls.style.marginRight = '20px';

        const debugDownloadBtn = document.createElement('button');
        debugDownloadBtn.textContent = 'CSV DL';
        debugDownloadBtn.style.backgroundColor = '#6c757d';
        debugDownloadBtn.style.color = 'white';
        debugDownloadBtn.style.border = 'none';
        debugDownloadBtn.style.padding = '0.5rem 1rem';
        debugDownloadBtn.style.borderRadius = '5px';
        debugDownloadBtn.style.cursor = 'pointer';
        debugDownloadBtn.addEventListener('click', () => {
            const completedTasks = taskTimings.filter(task => task.action === 'Task Completed');
            if (completedTasks.length > 0) {
                downloadCSV(completedTasks);
            } else {
                alert('データがありません。');
            }
        });

        const viewLoadersBtn = document.createElement('button');
        viewLoadersBtn.textContent = 'ローダー確認';
        viewLoadersBtn.style.backgroundColor = '#007bff';
        viewLoadersBtn.style.color = 'white';
        viewLoadersBtn.style.border = 'none';
        viewLoadersBtn.style.padding = '0.5rem 1rem';
        viewLoadersBtn.style.borderRadius = '5px';
        viewLoadersBtn.style.cursor = 'pointer';
        
        const loaderModal = document.getElementById('debug-loader-modal');
        viewLoadersBtn.addEventListener('click', () => {
            loaderModal.classList.remove('hidden');
            // プログレスバーのアニメーションを開始
            const bars = loaderModal.querySelectorAll('.progress-bar');
            bars.forEach(bar => {
                bar.style.width = '0';
                bar.style.transitionDuration = '0s';
                setTimeout(() => {
                    bar.style.transitionDuration = '2500ms';
                    bar.style.width = '100%';
                }, 50);
            });
        });
        loaderModal.querySelector('.modal-close-btn').addEventListener('click', () => loaderModal.classList.add('hidden'));

        debugControls.appendChild(debugDownloadBtn);
        debugControls.appendChild(viewLoadersBtn);
        headerRight.prepend(debugControls);

        completeTaskBtn.style.display = 'none';
        document.getElementById('header-task-description').innerHTML = '<span style="color: #666;">デバッグモード実行中</span>';
    }

    startExperimentBtn.addEventListener('click', () => {
        isDebugMode = false;
        showScreen(tutorialStartScreen);
    });

    enterDebugModeBtn.addEventListener('click', () => {
        isDebugMode = true;
        isTutorial = false;
        showScreen(ecSiteScreen);
        setupDebugUI();
        renderHome();
        currentCategory = 'home';
    });

    const backToLoaderBtn = document.getElementById('back-to-loader-selection-btn');
    if (backToLoaderBtn) {
        backToLoaderBtn.addEventListener('click', () => {
            const loaderModal = document.getElementById('debug-loader-modal');
            if (loaderModal) {
                loaderModal.classList.remove('hidden');
                // プログレスバーのアニメーションを開始
                const bars = loaderModal.querySelectorAll('.progress-bar');
                bars.forEach(bar => {
                    bar.style.width = '0';
                    bar.style.transitionDuration = '0s';
                    setTimeout(() => {
                        bar.style.transitionDuration = '2500ms';
                        bar.style.width = '100%';
                    }, 50);
                });
            }
        });
    }

    startTutorialBtn.addEventListener('click', () => {
        isTutorial = true;
        tutorialTrialIndex = 0;
        startTutorialTrial(tutorialTrialIndex);
    });

    startMainExperimentBtn.addEventListener('click', () => {
        isTutorial = false;
        currentPatternIndex = 0;
        startTrial(currentPatternIndex);
    });

    startTaskBtn.addEventListener('click', () => {
        // Create a temporary clone to manipulate for the header
        const tempDescription = document.getElementById('task-description').cloneNode(true);
        const descriptor = tempDescription.querySelector('.tutorial-descriptor');
        if (descriptor) {
            descriptor.remove();
        }
        const taskDescriptionHTML = tempDescription.innerHTML;

        const headerTaskDescription = document.getElementById('header-task-description');
        if (isTutorial) {
            headerTaskDescription.innerHTML = `チュートリアル ${tutorialTrialIndex + 1}/${tutorialTrials.length}: ${taskDescriptionHTML}`;
        } else {
            headerTaskDescription.innerHTML = `タスク ${currentPatternIndex + 1}/${experimentTrials.length}: ${taskDescriptionHTML}`;
        }
        
        const strongElements = headerTaskDescription.getElementsByTagName('strong');
        for (let strong of strongElements) {
            strong.style.backgroundColor = 'yellow';
            strong.style.color = '#000';
            strong.style.padding = '2px 4px';
            strong.style.borderRadius = '3px';
        }

        showScreen(ecSiteScreen);

        currentCategory = 'home';
        const homeLink = categoryNav.querySelector('[data-category="home"]');
        categoryNav.querySelector('.active')?.classList.remove('active');
        if (homeLink) homeLink.classList.add('active');
        if (homeVersion === 1) {
            renderHome();
        } else {
            renderHome2();
        }

        totalMouseDistance = 0;
        lastMouseX = 0;
        lastMouseY = 0;
        isMeasuringMouseDistance = true;
        taskStartTime = performance.now();
        accumulatedLoadingTime = 0;
        taskClickData = []; // Reset click data for new task
        cartItems = [];
        renderCart();
    });

    categoryNav.addEventListener('click', (e) => {
        if (e.target.tagName !== 'A') return;
        e.preventDefault();
        const newCategory = e.target.dataset.category;
        if (newCategory === currentCategory) return;

        const startTime = performance.now();
        const loaderType = getLoaderType();

        if (loaderType.startsWith('skeleton') && newCategory !== 'home') {
            productListContainer.style.display = 'grid';
            const categoryTitle = categoryNav.querySelector(`[data-category="${newCategory}"]`).textContent;
            const skeletonClass = loaderType === 'skeleton-color' ? 'skeleton-card color' : 'skeleton-card';
            
            // 表示する商品の数を取得し、その数だけスケルトンを生成する
            const numProducts = products[newCategory] ? products[newCategory].length : 8;
            
            const skeletonHtml = Array(numProducts).fill('').map(() => `
                <div class="${skeletonClass}">
                    <div class="skeleton-image"></div>
                    <div class="skeleton-content">
                        <div class="skeleton-text"></div>
                        <div class="skeleton-text short"></div>
                    </div>
                    <div class="skeleton-button"></div>
                </div>
            `).join('');
            productListContainer.innerHTML = `<h2>${categoryTitle}</h2>` + skeletonHtml;
        } else if (loaderType !== 'none') {
            showLoading();
        }

        categoryNav.querySelector('.active')?.classList.remove('active');
        e.target.classList.add('active');

        setTimeout(() => {
            if (loaderType !== 'none' && !loaderType.startsWith('skeleton')) hideLoading();
            if (newCategory === 'home') {
                if (homeVersion === 1) {
                    renderHome();
                } else {
                    renderHome2();
                }
            } else {
                renderProducts(newCategory);
            }
            const endTime = performance.now();
            if (!isTutorial) {
                accumulatedLoadingTime += loadingTimeMs;
                taskTimings.push({ action: 'Category Change', from: currentCategory, to: newCategory, loader: loaderType, time: endTime - startTime, simulatedDelay: loadingTimeMs });
            }
            currentCategory = newCategory;
        }, loadingTimeMs);
    });

    productListContainer.addEventListener('click', (e) => {
        const categoryCard = e.target.closest('.category-card');

        if (e.target.id === 'switch-home-layout-btn') {
            homeVersion = homeVersion === 1 ? 2 : 1;
            if (homeVersion === 1) {
                renderHome();
            } else {
                renderHome2();
            }
            return;
        }

        if (categoryCard) {
            const category = categoryCard.dataset.category;
            const categoryLink = categoryNav.querySelector(`[data-category="${category}"]`);
            if (categoryLink) {
                categoryLink.click();
            }
            return;
        }

        if (e.target.classList.contains('add-to-cart-btn')) {
            const productId = e.target.dataset.productId;
            const product = Object.values(products).flat().find(p => p.id === productId);
            if (product) {
                cartItems.push({ ...product, cartId: cartItemIdCounter++ });
                renderCart();
                showToast(`「${product.name}」をカートに追加しました！`);
            }
        }
    });

    cartSidebarBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-cart-item-btn')) {
            const cartId = parseInt(e.target.dataset.cartId, 10);
            cartItems = cartItems.filter(item => item.cartId !== cartId);
            renderCart();
        }
    });

    completeTaskBtn.addEventListener('click', () => {
        const currentTrial = isTutorial ? tutorialTrials[tutorialTrialIndex] : experimentTrials[currentPatternIndex];
        const requiredItems = (currentTrial.taskHTML.match(/<strong>(.*?)<\/strong>/g) || []).map(item => item.replace(/<\/?strong>/g, ''));
        const cartItemNames = cartItems.map(item => item.name);

        const areCartsEqual = requiredItems.length === cartItemNames.length && requiredItems.every(item => cartItemNames.includes(item));

        if (!areCartsEqual) {
            showToast('カートの中身が正しくありません。もう一度確認してください。');
            return;
        }

        isMeasuringMouseDistance = false; // Stop measuring for both tutorial and main task

        if (isTutorial) {
            // チュートリアルでもアンケート画面を表示する
            showScreen(surveyScreen);
            surveyTaskNumber.textContent = `チュートリアル ${tutorialTrialIndex + 1}`;
        } else {
            // 本番タスクではパフォーマンスを記録
            const taskDuration = performance.now() - taskStartTime;
            const pureTaskDuration = taskDuration - accumulatedLoadingTime;

            // --- 最適距離の計算 ---
            let optimalMouseDistance = 0;
            const requiredItemsForOptimal = (currentTrial.taskHTML.match(/<strong>(.*?)<\/strong>/g) || []).map(item => item.replace(/<\/?strong>/g, ''));
            
            const itemClickPos = requiredItemsForOptimal.map(itemName => {
                const clickRecord = taskClickData.find(c => c.target === `product-${itemName}`);
                return clickRecord ? clickRecord.pos : null;
            }).filter(pos => pos !== null);

            const completeClickPos = taskClickData.find(c => c.target === 'complete-task')?.pos;

            if (itemClickPos.length === requiredItemsForOptimal.length && completeClickPos && itemClickPos.length > 0) {
                let lastPos = itemClickPos[0];
                for (let i = 1; i < itemClickPos.length; i++) {
                    optimalMouseDistance += calculateDistance(lastPos, itemClickPos[i]);
                    lastPos = itemClickPos[i];
                }
                optimalMouseDistance += calculateDistance(lastPos, completeClickPos);
            }
            // --- 計算終了 ---

            taskTimings.push({
                executionOrder: currentPatternIndex + 1,
                originalTrialNumber: currentTrial.originalTrialNumber,
                action: 'Task Completed', 
                rageClicks: rageClickCount, 
                mouseDistance: totalMouseDistance,
                optimalMouseDistance: optimalMouseDistance,
                taskDuration: taskDuration, 
                totalLoadingTime: accumulatedLoadingTime,
                pureTaskDuration: pureTaskDuration,
                loaderType: selectedLoader, 
                simulatedLoadingTime: loadingTimeMs,
                taskSuccess: true,
                timestamp: new Date().toISOString()
            });
            console.log(`Trial ${currentPatternIndex + 1} completed. Data:`, taskTimings[taskTimings.length - 1]);
            
            showScreen(surveyScreen);
            surveyTaskNumber.textContent = currentPatternIndex + 1;
        }
    });

    function downloadCSV(data) {
        const allKeys = data.reduce((keys, obj) => {
            Object.keys(obj).forEach(key => {
                if (!keys.includes(key)) {
                    keys.push(key);
                }
            });
            return keys;
        }, []);

        const csv = [
            allKeys.join(','),
            ...data.map(row => allKeys.map(header => {
                let value = row[header];

                if (value === undefined || value === null) {
                    return '';
                }

                // Special handling for arrays to prevent unquoted commas
                if (Array.isArray(value)) {
                    // Join with a different separator, or quote the whole thing
                    // Let's quote the whole thing, which is more robust.
                    value = value.join(', '); // e.g., "ブロッコリー, クッキー"
                }
                
                let valueStr = String(value);

                // Quote the string if it contains a comma or a double quote
                if (valueStr.includes(',') || valueStr.includes('"')) {
                    // Escape existing double quotes by doubling them, then wrap the whole string in quotes.
                    valueStr = `"${valueStr.replace(/"/g, '""')}"`;
                }
                return valueStr;
            }).join(','))
        ].join('\n');

        // 文字化け対策としてBOMを追加
        const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'task_timings.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    downloadCsvBtn.addEventListener('click', () => {
        const completedTasks = taskTimings.filter(task => task.action === 'Task Completed');
        if (completedTasks.length > 0) {
            downloadCSV(completedTasks);
        } else {
            alert('データがありません。');
        }
    });

    function nextTaskLogic() {
        if (isTutorial) {
            tutorialTrialIndex++;
            if (tutorialTrialIndex < tutorialTrials.length) {
                startTutorialTrial(tutorialTrialIndex);
            } else {
                showScreen(tutorialCompleteScreen);
            }
        } else {
            currentPatternIndex++;
            if (currentPatternIndex < experimentTrials.length) {
                startTrial(currentPatternIndex);
            } else {
                showScreen(experimentCompleteScreen);
                console.log("Experiment finished. All data:", taskTimings);
            }
        }
        // フォームをリセット
        taskSurveyForm.reset();
        perceivedTimeInput.classList.remove('touched');
    }

    // VASスライダーのつまみ表示制御
    perceivedTimeInput.addEventListener('input', () => {
        perceivedTimeInput.classList.add('touched');
    });

    // アンケート送信ボタンのイベントリスナー
    taskSurveyForm.addEventListener('submit', (e) => {
        e.preventDefault(); // フォームのデフォルト送信を防止

        const discomfortRadio = document.querySelector('input[name="discomfort"]:checked');
        const reliabilityRadio = document.querySelector('input[name="reliability"]:checked');
        const isTouched = perceivedTimeInput.classList.contains('touched');

        // バリデーション
        if (!isTouched || !discomfortRadio || !reliabilityRadio) {
            let message = '回答に不足があります：\n';
            if (!isTouched) message += '・「体感的な読み込み時間の長さ」をスライダーで回答してください。\n';
            if (!discomfortRadio) message += '・「不快感」を選択してください。\n';
            if (!reliabilityRadio) message += '・「信頼性」を選択してください。';
            alert(message);
            return;
        }

        if (isTutorial) {
            nextTaskLogic();
            return;
        }

        const perceivedTime = parseFloat(perceivedTimeInput.value);
        const discomfort = parseInt(discomfortRadio.value, 10);
        const reliability = parseInt(reliabilityRadio.value, 10);

        // 最後のタスク完了レコードを見つける
        const lastCompletedTask = taskTimings.filter(t => t.action === 'Task Completed').pop();

        if (lastCompletedTask) {
            lastCompletedTask.perceivedTime = perceivedTime;
            lastCompletedTask.discomfort = discomfort;
            lastCompletedTask.reliability = reliability;
            console.log('Survey data added to task record:', lastCompletedTask);
        } else {
            console.error('Could not find the last completed task to add survey data to.');
        }
        
        showToast('アンケートを記録しました。');
        nextTaskLogic(); // 次のタスクへ進む
    });

    // 初期画面表示
    showScreen(startScreen);

    // --- ショートカット機能 ---
    const shortcutTask = urlParams.get('task');
    const shortcutCategory = urlParams.get('category');

    if (shortcutTask) {
        // タスク番号へのショートカット
        const taskIndex = parseInt(shortcutTask, 10) - 1; // 1-based to 0-based
        if (taskIndex >= 0 && taskIndex < experimentTrials.length) {
            console.log(`タスクへのショートカット: ${shortcutTask}`);
            isTutorial = false;
            currentPatternIndex = taskIndex;
            startTrial(currentPatternIndex);
        } else {
            console.error(`無効なタスク番号です: ${shortcutTask}`);
        }
    } else if (shortcutCategory && products[shortcutCategory]) {
        // カテゴリページへのショートカット
        console.log(`カテゴリへのショートカット: ${shortcutCategory}`);
        showScreen(ecSiteScreen); // ECサイト画面を直接表示
        renderProducts(shortcutCategory); // 指定されたカテゴリの商品をレンダリング

        // ナビゲーションのアクティブ状態を更新
        categoryNav.querySelector('.active')?.classList.remove('active');
        const categoryLink = categoryNav.querySelector(`[data-category="${shortcutCategory}"]`);
        if (categoryLink) {
            categoryLink.classList.add('active');
        }
        currentCategory = shortcutCategory;
    }
});

