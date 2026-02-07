// 支持的语言列表 - 可在客户端和服务端使用
export const locales = ['zh-CN', 'en'] as const;
export type Locale = (typeof locales)[number];

// 默认语言
export const defaultLocale: Locale = 'zh-CN';

// 语言显示名称
export const localeNames: Record<Locale, string> = {
    'zh-CN': '简体中文',
    'en': 'English',
};
