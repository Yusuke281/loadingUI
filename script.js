
document.addEventListener('DOMContentLoaded', () => {
    // --- 商品データ ---
    const products = {
        vegetables: [
            { id: 'v1', name: 'トマト', price: 150, image: 'images/tomato.jpg' },
            { id: 'v2', name: 'ピーマン', price: 120, image: 'images/bell-pepper.jpg' },
            { id: 'v3', name: 'ブロッコリー', price: 180, image: 'images/broccoli.jpg' },
            { id: 'v4', name: 'にんじん', price: 100, image: 'images/carrot.jpg' },
            { id: 'v5', name: 'カリフラワー', price: 200, image: 'images/cauliflower.jpg' },
            { id: 'v6', name: 'きゅうり', price: 90, image: 'images/cucumber.jpg' },
            { id: 'v7', name: 'なす', price: 130, image: 'images/eggplant.jpg' },
            { id: 'v8', name: 'ほうれん草', price: 160, image: 'images/spinach.jpg' }
        ],
        fruits: [
            { id: 'f1', name: 'りんご', price: 200, image: 'images/apple.jpg' },
            { id: 'f2', name: 'バナナ', price: 100, image: 'images/banana.jpg' },
            { id: 'f3', name: 'キウイ', price: 150, image: 'images/kiwi.jpg' },
            { id: 'f4', name: 'メロン', price: 1200, image: 'images/melon.jpg' },
            { id: 'f5', name: 'オレンジ', price: 180, image: 'images/orange.jpg' },
            { id: 'f6', name: 'パイナップル', price: 500, image: 'images/pineapple.jpg' },
            { id: 'f7', name: 'いちご', price: 450, image: 'images/strawberry.jpg' }
        ],
        sweets: [
            { id: 's1', name: 'ケーキ', price: 500, image: 'images/cake.jpg' },
            { id: 's2', name: 'チーズケーキ', price: 550, image: 'images/cheesecake.jpg' },
            { id: 's3', name: 'チョコレート', price: 250, image: 'images/chocolate.jpg' },
            { id: 's4', name: 'クッキー', price: 300, image: 'images/cookies.jpg' },
            { id: 's5', name: 'アイスクリーム', price: 200, image: 'images/ice-cream.jpg' },
            { id: 's6', name: 'プリン', price: 220, image: 'images/pudding.jpg' },
            { id: 's7', name: 'ポテトチップス', price: 150, image: 'images/potato-chips.jpg' }
        ],
        drinks: [
            { id: 'd1', name: '緑茶', price: 120, image: 'images/greentea.jpg' },
            { id: 'd2', name: 'コーラ', price: 150, image: 'images/cola.jpg' },
            { id: 'd3', name: 'オレンジジュース', price: 160, image: 'images/orange-juice.jpg' },
            { id: 'd4', name: 'コーヒー', price: 180, image: 'images/coffee.jpg' },
            { id: 'd5', name: '紅茶', price: 180, image: 'images/black-tea.jpg' },
            { id: 'd6', name: '牛乳', price: 140, image: 'images/milk.jpg' },
            { id: 'd7', name: '麦茶', price: 110, image: 'images/barley-tea.jpg' },
            { id: 'd8', name: 'スポーツドリンク', price: 150, image: 'images/sports-drink.jpg' }
        ]
    };

    const tutorialTrials = [
        { taskHTML: '<strong>トマト</strong>と<strong>りんご</strong>をカートに入れてください', loader: 'none', time: 3000 },
        { taskHTML: '<strong>ケーキ</strong>をカートに入れてください', loader: 'hourglass', time: 3000 },
        { taskHTML: '<strong>ほうれん草</strong>をカートに入れてください', loader: 'hourglass', time: 1500 }, // 短い例
        { taskHTML: '<strong>牛乳</strong>をカートに入れてください', loader: 'hourglass', time: 6000 },       // 長い例
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

    // --- 実験トライアル定義 (元の定義) ---
    const originalExperimentTrials = [
        {
            "taskHTML": "<strong>ブロッコリー</strong>と<strong>クッキー</strong>をカートに入れてください",
            "loader": "bar-color",
            "time": 5000
        },
        {
            "taskHTML": "<strong>なす</strong>と<strong>オレンジジュース</strong>をカートに入れてください",
            "loader": "bar",
            "time": 5000
        },
        {
            "taskHTML": "<strong>トマト</strong>と<strong>りんご</strong>をカートに入れてください",
            "loader": "none",
            "time": 1500
        },
        {
            "taskHTML": "<strong>キウイ</strong>と<strong>コーラ</strong>をカートに入れてください",
            "loader": "spinner",
            "time": 3000
        },
        {
            "taskHTML": "<strong>ピーマン</strong>と<strong>ケーキ</strong>をカートに入れてください",
            "loader": "none",
            "time": 3000
        },
        {
            "taskHTML": "<strong>ほうれん草</strong>と<strong>オレンジ</strong>をカートに入れてください",
            "loader": "skeleton-color",
            "time": 5000
        },
        {
            "taskHTML": "<strong>バナナ</strong>と<strong>チーズケーキ</strong>をカートに入れてください",
            "loader": "spinner",
            "time": 1500
        },
        {
            "taskHTML": "<strong>にんじん</strong>と<strong>コーヒー</strong>をカートに入れてください",
            "loader": "bar-color",
            "time": 1500
        },
        {
            "taskHTML": "<strong>ブロッコリー</strong>と<strong>緑茶</strong>をカートに入れてください",
            "loader": "none",
            "time": 5000
        },
        {
            "taskHTML": "<strong>きゅうり</strong>と<strong>クッキー</strong>をカートに入れてください",
            "loader": "bar",
            "time": 3000
        },
        {
            "taskHTML": "<strong>カリフラワー</strong>と<strong>メロン</strong>をカートに入れてください",
            "loader": "bar",
            "time": 1500
        },
        {
            "taskHTML": "<strong>プリン</strong>と<strong>緑茶</strong>をカートに入れてください",
            "loader": "skeleton",
            "time": 5000
        },
        {
            "taskHTML": "<strong>ピーマン</strong>と<strong>ポテトチップス</strong>をカートに入れてください",
            "loader": "spinner-color",
            "time": 3000
        },
        {
            "taskHTML": "<strong>キウイ</strong>と<strong>なす</strong>をカートに入れてください",
            "loader": "skeleton-color",
            "time": 1500
        },
        {
            "taskHTML": "<strong>チョコレート</strong>と<strong>にんじん</strong>をカートに入れてください",
            "loader": "spinner",
            "time": 5000
        },
        {
            "taskHTML": "<strong>チーズケーキ</strong>と<strong>緑茶</strong>をカートに入れてください",
            "loader": "skeleton-color",
            "time": 3000
        },
        {
            "taskHTML": "<strong>オレンジ</strong>と<strong>アイスクリーム</strong>をカートに入れてください",
            "loader": "skeleton",
            "time": 1500
        },
        {
            "taskHTML": "<strong>りんご</strong>と<strong>ケーキ</strong>をカートに入れてください",
            "loader": "spinner-color",
            "time": 5000
        },
        {
            "taskHTML": "<strong>トマト</strong>と<strong>いちご</strong>をカートに入れてください",
            "loader": "spinner-color",
            "time": 1500
        },
        {
            "taskHTML": "<strong>バナナ</strong>と<strong>チョコレート</strong>をカートに入れてください",
            "loader": "bar-color",
            "time": 3000
        },
        {
            "taskHTML": "<strong>パイナップル</strong>と<strong>ほうれん草</strong>をカートに入れてください",
            "loader": "skeleton",
            "time": 3000
        }
    ];

    // 元の課題番号を付与
    const experimentTrialsWithId = originalExperimentTrials.map((trial, index) => ({
        ...trial,
        originalTrialNumber: index + 1
    }));
    
    // シャッフルされた実験トライアル
    const experimentTrials = createConstrainedShuffle(experimentTrialsWithId);

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

    // --- デバッグモード ---
    let isDebugMode = false;

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
                    <h1>新鮮な食材を、<br>もっと手軽に。</h1>
                    <p>毎日の食卓を彩る、旬の野菜や果物を取り揃えています。</p>
                    <button class="hero-cta-btn" onclick="document.querySelector('[data-category=vegetables]').click()">商品を見る</button>
                </div>
            </div>

            <div class="home-section">
                <h2>カテゴリーから探す</h2>
                <div class="category-grid">
                    <div class="category-card" data-category="vegetables">
                        <img src="images/tomato.jpg" alt="野菜">
                        <span>野菜</span>
                    </div>
                    <div class="category-card" data-category="fruits">
                        <img src="images/strawberry.jpg" alt="果物">
                        <span>果物</span>
                    </div>
                    <div class="category-card" data-category="sweets">
                        <img src="images/cake.jpg" alt="お菓子・デザート">
                        <span>お菓子・デザート</span>
                    </div>
                    <div class="category-card" data-category="drinks">
                        <img src="images/greentea.jpg" alt="飲み物">
                        <span>飲み物</span>
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
        const featuredProducts = [...products.sweets.slice(0, 2), ...products.fruits.slice(0, 2)];
        productListContainer.innerHTML = `
            <div class="hero-section-2">
                <div class="hero-content-2">
                    <h1>新しい味覚、見つけよう。</h1>
                    <p>季節限定のスイーツや、産地直送のフルーツはいかがですか？</p>
                    <div class="search-bar-2">
                        <input type="search" placeholder="例: いちご, ケーキ">
                        <button type="button">検索</button>
                    </div>
                </div>
                <div class="hero-image-2">
                    <img src="images/cheesecake.jpg" alt="Hero Image">
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
        } else if (loaderType === 'hourglass') {
            loadingOverlay.innerHTML = '<div class="hourglass"></div>';
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
    startExperimentBtn.addEventListener('click', () => {
        showScreen(tutorialStartScreen);
    });

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
        const taskDescriptionHTML = taskDescription.innerHTML;
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
    }

    // アンケート送信ボタンのイベントリスナー
    taskSurveyForm.addEventListener('submit', (e) => {
        e.preventDefault(); // フォームのデフォルト送信を防止

        if (isTutorial) {
            nextTaskLogic();
            return;
        }

        const satisfactionRadio = document.querySelector('input[name="satisfaction"]:checked');

        // バリデーション
        if (!perceivedTimeInput.value || !satisfactionRadio) {
            alert('体感時間と満足度の両方を入力してください。');
            return;
        }

        const perceivedTime = parseFloat(perceivedTimeInput.value);
        const satisfaction = parseInt(satisfactionRadio.value, 10);

        // 最後のタスク完了レコードを見つける
        const lastCompletedTask = taskTimings.filter(t => t.action === 'Task Completed').pop();

        if (lastCompletedTask) {
            lastCompletedTask.perceivedTime = perceivedTime;
            lastCompletedTask.satisfaction = satisfaction;
            console.log('Survey data added to task record:', lastCompletedTask);
        } else {
            console.error('Could not find the last completed task to add survey data to.');
        }
        
        showToast('アンケートを記録しました。');
        nextTaskLogic(); // 次のタスクへ進む
    });

    // 初期画面表示
    showScreen(startScreen);

    // --- デバッグモード有効化 ---
    const urlParams = new URLSearchParams(window.location.search);
    isDebugMode = urlParams.get('debug') === 'true';

    if (isDebugMode) {
        const headerRight = document.querySelector('.header-right');
        if (headerRight) {
            // --- Debug Download Button ---
            const debugDownloadBtn = document.createElement('button');
            debugDownloadBtn.id = 'debug-download-btn';
            debugDownloadBtn.textContent = 'CSV DL (Debug)';
            debugDownloadBtn.style.marginLeft = '10px';
            debugDownloadBtn.style.backgroundColor = '#6c757d';
            debugDownloadBtn.style.color = 'white';
            debugDownloadBtn.style.border = 'none';
            debugDownloadBtn.style.padding = '0.6rem 1.2rem';
            debugDownloadBtn.style.fontSize = '0.9rem';
            debugDownloadBtn.style.fontWeight = 'bold';
            debugDownloadBtn.style.borderRadius = '5px';
            debugDownloadBtn.style.cursor = 'pointer';

            debugDownloadBtn.addEventListener('click', () => {
                const completedTasks = taskTimings.filter(task => task.action === 'Task Completed');
                if (completedTasks.length > 0) {
                    downloadCSV(completedTasks);
                } else {
                    alert('ダウンロード対象の完了済みタスクデータがありません。');
                }
            });
            headerRight.appendChild(debugDownloadBtn);

            // --- Loader Showcase Button & Modal Logic ---
            const viewLoadersBtn = document.createElement('button');
            viewLoadersBtn.id = 'view-loaders-btn';
            viewLoadersBtn.textContent = 'ローダー一覧';
            viewLoadersBtn.style.marginLeft = '10px';
            viewLoadersBtn.style.backgroundColor = '#007bff';
            viewLoadersBtn.style.color = 'white';
            viewLoadersBtn.style.border = 'none';
            viewLoadersBtn.style.padding = '0.6rem 1.2rem';
            viewLoadersBtn.style.fontSize = '0.9rem';
            viewLoadersBtn.style.fontWeight = 'bold';
            viewLoadersBtn.style.borderRadius = '5px';
            viewLoadersBtn.style.cursor = 'pointer';
            headerRight.appendChild(viewLoadersBtn);

            const loaderModal = document.getElementById('debug-loader-modal');
            const closeModalBtn = loaderModal.querySelector('.modal-close-btn');

            function showLoaderModal() {
                if (loaderModal) {
                    loaderModal.classList.remove('hidden');
                    // Animate progress bars when modal is shown
                    const progressBars = loaderModal.querySelectorAll('.progress-bar');
                    progressBars.forEach(bar => {
                        bar.style.transition = 'none';
                        bar.style.width = '0%';
                        setTimeout(() => {
                            bar.style.transition = 'width 2s ease-in-out';
                            bar.style.width = '100%';
                        }, 100);
                    });
                }
            }

            function hideLoaderModal() {
                if (loaderModal) loaderModal.classList.add('hidden');
            }

            viewLoadersBtn.addEventListener('click', showLoaderModal);
            closeModalBtn.addEventListener('click', hideLoaderModal);
            loaderModal.addEventListener('click', (e) => {
                if (e.target === loaderModal) {
                    hideLoaderModal();
                }
            });

            console.log("デバッグモードが有効です。");
        }
    }

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

