document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading');
    const micButton = document.getElementById('mic-button');

    // 用于存储对话历史的数组
    let conversationHistory = [];

    // 问题计数器
    let questionCount = 0;

    // 语音识别相关变量
    let recognition = null;
    let isRecording = false;

    // 初始化语音识别
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'zh-CN'; // 设置为中文
            
            recognition.onstart = () => {
                isRecording = true;
                micButton.classList.add('recording');
                micButton.innerHTML = '🔴';
                micButton.title = '正在录音，点击停止';
                messageInput.placeholder = '正在听取您的语音...';
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                messageInput.value = transcript;
                messageInput.focus();
            };
            
            recognition.onerror = (event) => {
                console.error('语音识别错误:', event.error);
                let errorMessage = '语音识别出错';
                switch(event.error) {
                    case 'no-speech':
                        errorMessage = '没有检测到语音，请重试';
                        break;
                    case 'network':
                        errorMessage = '网络错误，请检查网络连接';
                        break;
                    case 'not-allowed':
                        errorMessage = '请允许麦克风权限';
                        break;
                }
                addMessage('system', errorMessage);
                resetMicButton();
            };
            
            recognition.onend = () => {
                resetMicButton();
            };
        } else {
            micButton.disabled = true;
            micButton.title = '您的浏览器不支持语音识别';
            micButton.style.opacity = '0.5';
        }
    }

    // 重置麦克风按钮状态
    function resetMicButton() {
        isRecording = false;
        micButton.classList.remove('recording');
        micButton.innerHTML = '🎤';
        micButton.title = '点击开始语音输入';
        messageInput.placeholder = '输入您的问题或点击麦克风说话...';
    }

    // 麦克风按钮点击事件
    micButton.addEventListener('click', () => {
        if (!recognition) {
            addMessage('system', '您的浏览器不支持语音识别功能');
            return;
        }

        if (isRecording) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (error) {
                console.error('启动语音识别失败:', error);
                addMessage('system', '启动语音识别失败，请重试');
            }
        }
    });

    // 在页面加载时，自动获取AI的第一条欢迎消息
    function getInitialMessage() {
        showLoading(true);
        // 发送一个空消息，后端会识别为第一次请求并返回欢迎语
        fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: '你好', history: [] }) 
        })
        .then(response => response.json())
        .then(data => {
            showTypingIndicator(); // 显示正在输入指示器
            setTimeout(() => {
                hideTypingIndicator(); // 隐藏正在输入指示器
                if (data.response) {
                    addMessage('gemini', data.response, true); // 使用打字机效果
                    // 将AI的开场白存入历史
                    conversationHistory.push({ role: 'model', parts: [{ text: data.response }] });
                } else if (data.error) {
                    addMessage('gemini', `出错了: ${data.error}`, false); // 错误消息不使用打字机效果
                }
            }, 200); // 减少到200ms，让用户更快看到回复
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('gemini', '抱歉，连接服务器时发生错误。');
        })
        .finally(() => {
            showLoading(false);
        });
    }

    // 表单提交事件
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const userMessage = messageInput.value.trim();
        if (userMessage === '') return;

        // 在界面上显示用户消息
        addMessage('user', userMessage);
        // 将用户消息存入历史 (注意：这里不需要立即添加，因为后端会处理)
        // conversationHistory.push({ role: 'user', parts: [{ text: userMessage }] });

        messageInput.value = '';
        showLoading(true);
        showTypingIndicator(); // 立即显示思考指示器

        // 检查用户是否要求填写表单
        const formKeywords = ['填写表单', '填表', '表单', '填写信息', '直接填写'];
        if (formKeywords.some(keyword => userMessage.includes(keyword))) {
            // 切换到表单界面
            switchToForm();
            return;
        }

        // 发送消息到后端
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage, history: conversationHistory }),
        })
        .then(response => response.json())
        .then(data => {
            // 思考指示器已经在显示，现在改为输入指示器
            const typingElement = document.getElementById('typing-indicator');
            if (typingElement) {
                typingElement.innerHTML = '蕾拉酱的AI小助理正在输入<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
            }
            setTimeout(() => {
                hideTypingIndicator(); // 隐藏正在输入指示器
                if (data.response) {
                    addMessage('gemini', data.response, true); // 使用打字机效果
                    // 将用户消息和AI回复都存入历史
                    conversationHistory.push({ role: 'user', parts: [{ text: userMessage }] });
                    conversationHistory.push({ role: 'model', parts: [{ text: data.response }] });
                    
                    // 增加问题计数器
                    questionCount++;
                    console.log('问题计数:', questionCount);
                    
                    // 每5个问题显示注册弹窗
                    if (questionCount % 5 === 0) {
                        setTimeout(() => {
                            showRegistrationPopup();
                        }, 2000); // 等待2秒后显示弹窗，让用户先看完回复
                    }
                } else if (data.error) {
                    addMessage('gemini', `出错了: ${data.error}`, false); // 错误消息不使用打字机效果
                }
            }, 200); // 减少到200ms，让用户更快看到回复
        })
        .catch(error => {
            console.error('Error:', error);
            hideTypingIndicator(); // 隐藏思考指示器
            addMessage('gemini', '抱歉，与蕾拉酱的AI小助理通信时发生错误。');
        })
        .finally(() => {
            showLoading(false);
        });
    });

    // 在聊天窗口中添加消息
    function addMessage(sender, text, useTypewriter = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        chatMessages.appendChild(messageElement);
        
        if (useTypewriter && sender === 'gemini') {
            // 使用打字机效果显示AI回复，并在完成后添加选择按钮
            typewriterEffect(messageElement, text, 20, () => {
                // 打字机效果完成后的回调，添加选择按钮
                if (sender === 'gemini') {
                    addChoiceButtons(messageElement, text);
                }
            });
        } else {
            // 立即显示消息（用户消息和系统消息）
            displayFormattedText(messageElement, text);
        // 检查是否包含选择题并添加按钮
        if (sender === 'gemini') {
            addChoiceButtons(messageElement, text);
            }
        }
        
        // 自动滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 格式化并显示文本
    function displayFormattedText(element, text) {
        // 移除选择题标记，只显示问题文本
        let cleanText = text.replace(/\[CHOICES\][\s\S]*?\[\/CHOICES\]/g, '');
        
        // 简单的Markdown转换：将**text**转换为<b>text</b>, *text*转换为<i>text</i>, \n转换为<br>
        let formattedText = cleanText
            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/\*(.*?)\*/g, '<i>$1</i>')
            .replace(/\n/g, '<br>');

        element.innerHTML = formattedText;
    }
    
    // 添加选择题按钮
    function addChoiceButtons(messageElement, text) {
        const choicesMatch = text.match(/\[CHOICES\]([\s\S]*?)\[\/CHOICES\]/);
        if (choicesMatch) {
            const choicesText = choicesMatch[1].trim();
            const choices = choicesText.split('|').map(choice => choice.trim());
            
            // 创建按钮容器
            const buttonsContainer = document.createElement('div');
            buttonsContainer.classList.add('choice-buttons');
            
            choices.forEach(choice => {
                const button = document.createElement('button');
                button.classList.add('choice-btn');
                button.textContent = choice;
                button.onclick = () => handleChoiceClick(choice, buttonsContainer);
                buttonsContainer.appendChild(button);
            });
            
            messageElement.appendChild(buttonsContainer);
        }
    }
    
    // 处理选择按钮点击
    function handleChoiceClick(choice, buttonsContainer) {
        // 检查是否是表单相关选项
        if (choice === '填写表单' || choice === '直接填写表单' || choice === '需要修改信息') {
            // 切换到表单界面
            switchToForm();
            // 禁用按钮并高亮
            const buttons = buttonsContainer.querySelectorAll('.choice-btn');
            buttons.forEach(btn => {
                btn.disabled = true;
                if (btn.textContent === choice) {
                    btn.classList.add('selected');
                }
            });
            return;
        }
        
        // 禁用所有按钮并高亮选中的按钮
        const buttons = buttonsContainer.querySelectorAll('.choice-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            if (btn.textContent === choice) {
                btn.classList.add('selected');
            }
        });
        
        // 自动发送选择的答案
        messageInput.value = choice;
        chatForm.dispatchEvent(new Event('submit'));
    }
    
    // 切换到表单界面
    function switchToForm() {
        const chatContainer = document.getElementById('chat-container');
        const formContainer = document.getElementById('form-container');
        
        if (chatContainer && formContainer) {
            chatContainer.style.display = 'none';
            formContainer.style.display = 'flex';
            
            // 预填表单数据
            prefillFormData();
        }
    }
    
    // 切换回聊天界面
    window.switchToChat = function() {
        const chatContainer = document.getElementById('chat-container');
        const formContainer = document.getElementById('form-container');
        
        if (chatContainer && formContainer) {
            chatContainer.style.display = 'flex';
            formContainer.style.display = 'none';
        }
    }

    // 显示AI正在输入的指示器
    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('message', 'gemini-message', 'typing-indicator-message');
        typingElement.id = 'typing-indicator';
        typingElement.innerHTML = '蕾拉酱的AI小助理正在思考中<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 隐藏AI正在输入的指示器
    function hideTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }

    // 打字机效果
    function typewriterEffect(element, text, speed = 20, callback = null) {
        // 先格式化文本，但保留选择题标记用于后续处理
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/\*(.*?)\*/g, '<i>$1</i>')
            .replace(/\n/g, '<br>');
        
        // 移除选择题标记，只显示问题文本
        let displayText = formattedText.replace(/\[CHOICES\][\s\S]*?\[\/CHOICES\]/g, '');

        element.innerHTML = '';
        let index = 0;
        let currentText = '';
        
        // 添加光标
        const cursor = document.createElement('span');
        cursor.className = 'typing-cursor';
        cursor.innerHTML = '|';
        element.appendChild(cursor);

        const typeInterval = setInterval(() => {
            if (index < displayText.length) {
                // 处理HTML标签
                if (displayText[index] === '<') {
                    // 找到完整的HTML标签
                    let tagEnd = displayText.indexOf('>', index);
                    if (tagEnd !== -1) {
                        currentText += displayText.substring(index, tagEnd + 1);
                        index = tagEnd + 1;
                    } else {
                        currentText += displayText[index];
                        index++;
                    }
                } else {
                    currentText += displayText[index];
                    index++;
                }
                
                // 更新显示内容
                element.innerHTML = currentText + '<span class="typing-cursor">|</span>';
                
                // 自动滚动到底部
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                // 打字完成，移除光标
                element.innerHTML = currentText;
                clearInterval(typeInterval);
                
                // 执行回调函数（如果提供了的话）
                if (callback && typeof callback === 'function') {
                    callback();
                }
            }
        }, speed);
    }

    // 控制加载指示器的显示
    function showLoading(isLoading) {
        loadingIndicator.style.display = isLoading ? 'flex' : 'none';
    }
    
    // 显示注册弹窗
    function showRegistrationPopup() {
        // 检查是否已经显示过弹窗（避免重复显示）
        if (document.getElementById('registration-popup')) {
            return;
        }
        
        // 创建弹窗遮罩
        const overlay = document.createElement('div');
        overlay.id = 'registration-popup';
        overlay.className = 'popup-overlay';
        
        // 创建弹窗内容
        const popup = document.createElement('div');
        popup.className = 'popup-content';
        popup.innerHTML = `
            <div class="popup-header">
                <h3>🎵 同学，问了这么多问题</h3>
                <button class="popup-close" onclick="closeRegistrationPopup()">&times;</button>
            </div>
            <div class="popup-body">
                <p>要不要注册一个账号啊？<br>以后就可以用这个平台管理你的留学咯～</p>
                <div class="popup-buttons">
                    <button class="btn-primary" onclick="handleRegistration()">好的，注册账号</button>
                    <button class="btn-secondary" onclick="closeRegistrationPopup()">稍后再说</button>
                </div>
            </div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // 点击遮罩区域关闭弹窗
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closeRegistrationPopup();
            }
        });
        
        // 添加动画效果
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);
    }
    
    // 关闭注册弹窗
    window.closeRegistrationPopup = function() {
        const popup = document.getElementById('registration-popup');
        if (popup) {
            popup.classList.remove('show');
            setTimeout(() => {
                popup.remove();
            }, 300);
        }
    }
    
    // 处理注册
    window.handleRegistration = function() {
        // 直接跳转到注册页面
        closeRegistrationPopup();
        window.location.href = '/register';
    }
    
    // 显示表单模态框
    function showFormModal() {
        const modal = document.getElementById('form-modal');
        if (modal) {
            // 预填表单数据
            prefillFormData();
            
            modal.classList.add('show');
            document.body.style.overflow = 'hidden'; // 防止背景滚动
        }
    }
    
    // 关闭表单模态框
    window.closeFormModal = function() {
        const modal = document.getElementById('form-modal');
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = ''; // 恢复滚动
        }
    }
    
    // 预填表单数据
    function prefillFormData() {
        // 从session或已收集的数据中获取用户信息
        fetch('/get_user_profile')
            .then(response => response.json())
            .then(data => {
                if (data.user_profile) {
                    const profile = data.user_profile;
                    
                    // 预填单选字段
                    const singleFields = ['name', 'age_range', 'gender', 'current_grade', 'current_major', 'intake_term', 'budget_cny_range', 'contact_method', 'notes'];
                    singleFields.forEach(field => {
                        const element = document.getElementById(`form-${field}`);
                        if (element && profile[field]) {
                            element.value = profile[field];
                        }
                    });
                    
                    // 预填多选字段 - countries
                    if (profile.countries && Array.isArray(profile.countries)) {
                        const countriesSelect = document.getElementById('form-countries');
                        if (countriesSelect) {
                            Array.from(countriesSelect.options).forEach(option => {
                                if (profile.countries.includes(option.value)) {
                                    option.selected = true;
                                }
                            });
                        }
                    }
                    
                    // 预填多选字段 - target_major
                    if (profile.target_major) {
                        const targetMajorSelect = document.getElementById('form-target_major');
                        if (targetMajorSelect) {
                            const majors = Array.isArray(profile.target_major) ? profile.target_major : [profile.target_major];
                            Array.from(targetMajorSelect.options).forEach(option => {
                                if (majors.includes(option.value)) {
                                    option.selected = true;
                                }
                            });
                        }
                    }
                    
                    // 预填复选框 - special_requests
                    if (profile.special_requests && Array.isArray(profile.special_requests)) {
                        profile.special_requests.forEach(request => {
                            const checkbox = document.querySelector(`#form-modal input[name="special_requests"][value="${request}"]`);
                            if (checkbox) {
                                checkbox.checked = true;
                            }
                        });
                    }
                }
            })
            .catch(error => {
                console.error('获取用户信息失败:', error);
            });
    }
    
    // 处理表单提交 - 移除重复的DOMContentLoaded监听器
    function initFormSubmission() {
        const embeddedForm = document.getElementById('embedded-form');
        if (embeddedForm && !embeddedForm.hasAttribute('data-listener-added')) {
            embeddedForm.setAttribute('data-listener-added', 'true');
            embeddedForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                console.log('表单提交开始...');
                
                // 收集表单数据
                const formData = new FormData(embeddedForm);
                const data = {};
                
                // 处理单选字段
                for (let [key, value] of formData.entries()) {
                    if (key === 'special_requests' || key === 'countries' || key === 'target_major') {
                        if (!data[key]) data[key] = [];
                        data[key].push(value);
                    } else {
                        data[key] = value;
                    }
                }
                
                console.log('收集到的表单数据:', data);
                
                // 发送到后端
                fetch('/submit_form', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    console.log('服务器响应状态:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP错误! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('服务器响应结果:', result);
                    if (result.success) {
                        // 显示数据库保存状态
                        if (result.database_saved) {
                            console.log('✅ 用户数据已成功保存到数据库');
                        } else {
                            console.warn('⚠️ 数据库保存失败:', result.database_error);
                        }
                        
                        // 切换回聊天界面
                        switchToChat();
                        
                        // 添加AI总结消息
                        addMessage('gemini', result.summary, true);
                        
                        // 更新对话历史
                        conversationHistory.push({ 
                            role: 'model', 
                            parts: [{ text: result.summary }] 
                        });
                    } else {
                        alert('提交失败: ' + (result.message || '请重试'));
                    }
                })
                .catch(error => {
                    console.error('表单提交失败:', error);
                    alert('提交失败: ' + error.message);
                });
            });
        }
    }
    
    // 移动端优化函数
    function initMobileOptimizations() {
        // 检测移动设备
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            // 防止iOS Safari缩放
            document.addEventListener('touchstart', function(event) {
                if (event.touches.length > 1) {
                    event.preventDefault();
                }
            }, { passive: false });
            
            // 处理虚拟键盘显示/隐藏
            let lastHeight = window.innerHeight;
            
            window.addEventListener('resize', function() {
                const currentHeight = window.innerHeight;
                const heightDifference = lastHeight - currentHeight;
                
                // 如果高度减少超过150px，可能是键盘显示
                if (heightDifference > 150) {
                    document.body.classList.add('keyboard-open');
                    // 确保输入框可见
                    setTimeout(() => {
                        messageInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                } else if (heightDifference < -150) {
                    // 键盘隐藏
                    document.body.classList.remove('keyboard-open');
                }
                
                lastHeight = currentHeight;
            });
            
            // 输入框获得焦点时的处理
            messageInput.addEventListener('focus', function() {
                setTimeout(() => {
                    // 滚动到输入框
                    this.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    // 滚动聊天消息到底部
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 300);
            });
            
            // 防止双击缩放
            let lastTouchEnd = 0;
            document.addEventListener('touchend', function(event) {
                const now = (new Date()).getTime();
                if (now - lastTouchEnd <= 300) {
                    event.preventDefault();
                }
                lastTouchEnd = now;
            }, false);
        }
    }
    
    // 初始化语音识别
    initSpeechRecognition();
    
    // 移动端优化
    initMobileOptimizations();
    
    // 初始化表单提交处理
    initFormSubmission();
    
    // 检查用户登录状态并显示用户信息（这会处理初始消息显示）
    checkUserLoginStatus();
    
    // 用户菜单控制函数
    window.toggleUserMenu = function() {
        const userMenu = document.getElementById('user-menu');
        if (userMenu) {
            userMenu.style.display = userMenu.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    // 点击其他地方关闭用户菜单
    document.addEventListener('click', function(event) {
        const userMenu = document.getElementById('user-menu');
        const userMenuBtn = event.target.closest('.user-menu-btn');
        
        if (userMenu && !userMenuBtn && userMenu.style.display === 'block') {
            userMenu.style.display = 'none';
        }
    });
    
    // 检查用户登录状态
    function checkUserLoginStatus() {
        fetch('/api/user_info')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Not logged in');
            })
            .then(data => {
                if (data.success && data.user) {
                    showUserInfo(data.user);
                    // 用户已登录，更新用户profile信息
                    updateUserProfileFromLogin(data.user);
                    // 加载聊天历史
                    loadChatHistory();
                }
            })
            .catch(error => {
                // 用户未登录，隐藏用户信息栏
                hideUserInfo();
                // 未登录用户显示初始欢迎消息
                getInitialMessage();
            });
    }
    
    // 从登录信息更新用户profile
    function updateUserProfileFromLogin(user) {
        // 获取当前的用户profile
        fetch('/get_user_profile')
            .then(response => response.json())
            .then(data => {
                const currentProfile = data.user_profile || {};
                
                // 如果profile中没有姓名，则从登录用户信息中获取
                if (!currentProfile.name && (user.display_name || user.username)) {
                    console.log('✅ 已登录用户信息已自动填充到profile');
                }
            })
            .catch(error => {
                console.error('获取用户profile失败:', error);
            });
    }
    
    // 显示用户信息
    function showUserInfo(user) {
        const userInfoBar = document.getElementById('user-info-bar');
        const userName = document.getElementById('user-name');
        const userAvatar = document.querySelector('.user-avatar');
        
        if (userInfoBar && userName) {
            // 设置用户名
            userName.textContent = user.display_name || user.username || '用户';
            
            // 如果有头像URL，可以设置头像
            if (user.avatar_url) {
                userAvatar.innerHTML = `<img src="${user.avatar_url}" alt="头像" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
            } else {
                // 使用用户名首字母作为头像
                const firstChar = (user.display_name || user.username || '用').charAt(0).toUpperCase();
                userAvatar.textContent = firstChar;
            }
            
            // 显示用户信息栏
            userInfoBar.style.display = 'flex';
            
            console.log('✅ 用户已登录:', user.display_name || user.username);
        }
    }
    
    // 隐藏用户信息
    function hideUserInfo() {
        const userInfoBar = document.getElementById('user-info-bar');
        if (userInfoBar) {
            userInfoBar.style.display = 'none';
        }
    }
    
    // 加载聊天历史
    function loadChatHistory() {
        fetch('/api/chat_history')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to load chat history');
            })
            .then(data => {
                if (data.success && data.chat_history.length > 0) {
                    console.log(`✅ 加载了 ${data.message_count} 条历史消息`);
                    
                    // 显示历史消息
                    displayChatHistory(data.chat_history);
                    
                    // 更新对话历史供AI使用
                    conversationHistory = data.conversation_history;
                    
                    // 显示"继续对话"提示
                    addMessage('system', '📚 已加载历史聊天记录，你可以继续之前的对话');
                    
                } else {
                    // 没有历史记录，显示初始欢迎消息
                    console.log('📝 没有历史聊天记录，显示欢迎消息');
                    getInitialMessage();
                }
            })
            .catch(error => {
                console.error('加载聊天历史失败:', error);
                // 加载失败，显示初始欢迎消息
                getInitialMessage();
            });
    }
    
    // 显示聊天历史
    function displayChatHistory(chatHistory) {
        // 清空当前聊天消息
        chatMessages.innerHTML = '';
        
        // 按时间顺序显示历史消息
        chatHistory.forEach(msg => {
            const sender = msg.sender === 'user' ? 'user' : 'gemini';
            addMessage(sender, msg.message, false); // 不使用打字机效果
        });
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 注意：不再在这里调用getInitialMessage()，因为现在由checkUserLoginStatus()处理
});
