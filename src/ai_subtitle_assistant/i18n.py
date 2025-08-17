import gettext
import os
import locale
import sys


def get_system_language():
    """
    获取操作系统的语言设置
    """
    try:
        # 获取默认的区域设置
        lang, encoding = locale.getdefaultlocale()
        if lang:
            return lang.split("_")[0]
    except Exception:
        pass
    return "en"  # 默认为英语


def get_locale_dir():
    """
    获取locale目录的正确路径，无论是在开发环境还是安装后都能正确工作
    """
    # 尝试获取包的安装路径
    try:
        # 当包被安装时，__file__指向安装位置
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        installed_locale_dir = os.path.join(package_dir, "locales")

        # 检查安装目录下的locale是否存在
        if os.path.exists(installed_locale_dir):
            return installed_locale_dir
    except Exception:
        pass

    # 如果安装目录下没有找到，尝试开发环境的路径
    try:
        # 开发环境中的相对路径
        dev_locale_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "locales",
        )
        if os.path.exists(dev_locale_dir):
            return dev_locale_dir
    except Exception:
        pass

    # 如果都找不到，返回默认路径
    return "locales"


# 设置本地化目录
localedir = get_locale_dir()

# 获取系统语言并设置为当前语言
current_language = get_system_language()

# 创建一个翻译实例
try:
    translation = gettext.translation(
        "messages", localedir, languages=[current_language], fallback=True
    )
except FileNotFoundError:
    # 如果找不到特定语言的 .mo 文件，则回退到不进行翻译
    translation = gettext.NullTranslations()


def set_language(language):
    """
    设置当前语言
    """
    global translation, current_language
    current_language = language
    try:
        print(f"正在加载语言: {language}", file=sys.stderr)
        print(f"翻译文件目录: {localedir}", file=sys.stderr)
        translation = gettext.translation(
            "messages", localedir, languages=[current_language], fallback=True
        )
        print("成功加载翻译文件", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"未找到翻译文件: {e}", file=sys.stderr)
        translation = gettext.NullTranslations()


def _(message):
    """
    获取翻译后的字符串
    """
    return translation.gettext(message)
