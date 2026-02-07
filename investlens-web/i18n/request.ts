import { getRequestConfig } from 'next-intl/server';
import { cookies, headers } from 'next/headers';
import { locales, defaultLocale, type Locale } from './config';

export default getRequestConfig(async () => {
    // 从 cookie 或 headers 获取用户偏好语言
    const cookieStore = await cookies();
    const headersList = await headers();

    let locale: Locale = defaultLocale;

    // 优先从 cookie 读取
    const cookieLocale = cookieStore.get('NEXT_LOCALE')?.value as Locale;
    if (cookieLocale && locales.includes(cookieLocale)) {
        locale = cookieLocale;
    } else {
        // 读取浏览器语言偏好
        const acceptLanguage = headersList.get('accept-language');
        if (acceptLanguage) {
            const browserLocale = acceptLanguage.split(',')[0].split('-')[0];
            if (browserLocale === 'zh') {
                locale = 'zh-CN';
            } else if (browserLocale === 'en') {
                locale = 'en';
            }
        }
    }

    return {
        locale,
        messages: (await import(`../messages/${locale}.json`)).default,
    };
});
