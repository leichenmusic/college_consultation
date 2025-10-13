#!/usr/bin/env python3
"""
AI对话优化模块
提供智能对话分析和优化功能
"""

def analyze_user_intent(user_message, chat_history, user_profile):
    """分析用户意图和需求优先级"""
    user_msg_lower = user_message.lower()
    
    # 意图分类
    intent_keywords = {
        'school_recommendation': ['推荐学校', '哪个学校', '院校推荐', '学校选择', '好学校', '哪所学校', '学校排名'],
        'application_help': ['申请', '如何申请', '申请流程', '申请材料', 'deadline', '申请要求', '怎么申请'],
        'portfolio_guidance': ['作品集', '曲目', '录音', '录制', '演奏', '作品', '曲目选择', '录制要求'],
        'country_advice': ['哪个国家', '国家选择', '美国', '英国', '德国', '意大利', '去哪个国家', '国家推荐'],
        'budget_planning': ['费用', '预算', '多少钱', '花费', '奖学金', '学费', '生活费', '成本'],
        'timeline_planning': ['时间', '什么时候', '几月', '规划', '时间线', '申请时间', '截止时间'],
        'major_guidance': ['专业', '什么专业', '选专业', '声乐', '器乐', '作曲', '专业选择', '哪个专业'],
        'exam_preparation': ['考试', '语言考试', '托福', '雅思', '准备考试', '考试要求'],
        'just_chatting': ['你好', 'hi', 'hello', '聊天', '随便聊聊', '怎么样', '不错']
    }
    
    detected_intents = []
    for intent, keywords in intent_keywords.items():
        if any(keyword in user_msg_lower for keyword in keywords):
            detected_intents.append(intent)
    
    # 分析对话历史，判断用户参与度
    engagement_level = 'low'
    if len(chat_history) > 3:
        engagement_level = 'medium'
    if len(chat_history) > 8:
        engagement_level = 'high'
    
    # 分析信息完整度
    total_fields = 11
    filled_fields = len([v for v in user_profile.values() if v and v != '' and v != []])
    profile_completeness = filled_fields / total_fields
    
    # 判断是否应该继续收集信息
    should_collect_info = (
        profile_completeness < 0.6 and 
        engagement_level != 'low' and 
        'just_chatting' not in detected_intents
    )
    
    return {
        'intents': detected_intents,
        'primary_intent': detected_intents[0] if detected_intents else 'information_collection',
        'engagement_level': engagement_level,
        'profile_completeness': profile_completeness,
        'should_collect_info': should_collect_info,
        'filled_fields': filled_fields,
        'total_fields': total_fields
    }

def get_smart_next_question(user_profile, user_intent_analysis):
    """根据用户档案和意图分析，智能决定下一个问题"""
    
    # 如果用户主要意图不是信息收集，直接回应其需求
    if user_intent_analysis['primary_intent'] != 'information_collection':
        return None, None  # 让AI直接回应用户的具体问题
    
    # 定义字段优先级（根据用户意图调整）
    field_priority = {
        'school_recommendation': ['countries', 'target_major', 'budget_cny_range', 'current_grade'],
        'application_help': ['target_major', 'countries', 'intake_term', 'current_grade'],
        'portfolio_guidance': ['current_major', 'target_major', 'current_grade'],
        'budget_planning': ['budget_cny_range', 'countries', 'target_major'],
        'default': ['current_grade', 'current_major', 'target_major', 'countries', 'intake_term', 'budget_cny_range']
    }
    
    # 根据主要意图选择优先级
    priority_fields = field_priority.get(
        user_intent_analysis['primary_intent'], 
        field_priority['default']
    )
    
    # 找到第一个缺失的重要字段
    for field in priority_fields:
        if not user_profile.get(field):
            return get_question_for_field(field)
    
    # 如果重要字段都有了，检查其他字段
    all_fields = ['name', 'age_range', 'gender', 'current_grade', 'current_major', 
                  'target_major', 'countries', 'intake_term', 'budget_cny_range', 
                  'special_requests', 'contact_method']
    
    for field in all_fields:
        if not user_profile.get(field):
            return get_question_for_field(field)
    
    return None, None  # 所有信息都收集完了

def get_question_for_field(field):
    """为特定字段生成问题和选项"""
    questions = {
        'name': ("请问怎么称呼你？", "直接输入姓名|跳过"),
        'age_range': ("你目前多大了？", "≤15|16–18|19–22|23–26|27–30|30+|跳过"),
        'gender': ("性别是？", "女|男|不便透露|跳过"),
        'current_grade': ("你现在在读什么学段？", "初中|高中|本科在读|本科已毕业|研究生|在职提升|跳过"),
        'current_major': ("你目前学的是什么音乐专业？", "声乐|器乐|作曲/指挥/音乐教育|音乐技术/音乐产业|跳过"),
        'target_major': ("你想申请什么专业？", "声乐表演|音乐剧|器乐表演|作曲/编曲|指挥|音乐教育|音乐科技/制作|音乐商业/管理|跳过"),
        'countries': ("想去哪个国家留学？", "美国|英国|意大利|德国|法国|加拿大|澳大利亚|跳过"),
        'intake_term': ("计划什么时候入学？", "2025 Fall|2026 Fall|2027 Fall|2026 Spring|待定|跳过"),
        'budget_cny_range': ("大概的预算范围是？", "≤30万|30–60万|60–100万|100–150万|≥150万|待定|跳过"),
        'special_requests': ("有什么特殊需求吗？", "学校推荐|国家推荐|奖学金策略|作品集指导|面试辅导|暂无|跳过"),
        'contact_method': ("希望通过什么方式联系你？", "邮箱|微信|手机|都可以|稍后提供|跳过")
    }
    
    return questions.get(field, ("还有其他信息需要了解吗？", "继续|跳过"))

def generate_optimized_prompt(user_message, user_profile, chat_history, user_intent_analysis):
    """生成优化的AI提示词"""
    
    # 如果用户有明确的咨询意图，优先回应
    if user_intent_analysis['primary_intent'] != 'information_collection':
        return generate_consultation_prompt(user_message, user_profile, user_intent_analysis)
    
    # 如果信息收集度较高或用户参与度低，转向咨询模式
    if (user_intent_analysis['profile_completeness'] > 0.6 or 
        user_intent_analysis['engagement_level'] == 'low'):
        return generate_consultation_prompt(user_message, user_profile, user_intent_analysis)
    
    # 否则继续信息收集，但要更智能
    next_question, choices = get_smart_next_question(user_profile, user_intent_analysis)
    
    if not next_question:
        # 信息收集完成，转向咨询
        return generate_consultation_prompt(user_message, user_profile, user_intent_analysis)
    
    return f"""
你是「蕾拉酱的AI小助手」，音乐留学顾问。用户刚说："{user_message}"

当前用户信息完整度：{user_intent_analysis['filled_fields']}/{user_intent_analysis['total_fields']}

请：
1. 简短回应用户的话（1句话）
2. 问下一个问题：{next_question}

[CHOICES]
{choices}
[/CHOICES]

要求：总共不超过3行，语气友好自然。
"""

def generate_consultation_prompt(user_message, user_profile, user_intent_analysis):
    """生成咨询模式的提示词"""
    
    intent_responses = {
        'school_recommendation': "根据用户信息推荐2-3所合适的音乐院校，简要说明推荐理由",
        'application_help': "提供具体的申请指导，包括材料准备和时间规划",
        'portfolio_guidance': "给出作品集准备的具体建议，包括曲目选择和录制要求",
        'country_advice': "比较不同国家的优势，给出选择建议",
        'budget_planning': "分析留学费用构成，提供预算规划建议",
        'timeline_planning': "制定详细的申请时间线",
        'major_guidance': "分析不同专业的特点和就业前景",
        'exam_preparation': "提供语言考试和专业考试的准备建议"
    }
    
    primary_intent = user_intent_analysis['primary_intent']
    response_guidance = intent_responses.get(primary_intent, "根据用户问题提供专业的音乐留学建议")
    
    return f"""
你是「蕾拉酱的AI小助手」，专业音乐留学顾问。

用户问题："{user_message}"
用户信息：{user_profile}
用户主要需求：{primary_intent}

请：
1. {response_guidance}
2. 控制在5行以内，要点明确
3. 提供3-4个相关的后续选择按钮

[CHOICES]
根据回答内容提供相关选择|查看更多|预约咨询|填写详细表单
[/CHOICES]

要求：专业、简洁、实用，避免空话套话。
"""

if __name__ == "__main__":
    # 测试代码
    test_profile = {'name': '小明', 'current_grade': '本科在读'}
    test_history = [{'role': 'user', 'content': '你好'}]
    test_message = "我想申请美国的音乐学院"
    
    analysis = analyze_user_intent(test_message, test_history, test_profile)
    print("Intent Analysis:", analysis)
    
    prompt = generate_optimized_prompt(test_message, test_profile, test_history, analysis)
    print("Generated Prompt:", prompt)
