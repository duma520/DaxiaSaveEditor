# -*- coding: utf-8 -*-
"""大侠狂想曲 存档修改器 —— 主程序"""
__version__ = "1.3.0"
APP_NAME = "大侠狂想曲存档修改器"

import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QPixmap, QIcon, QFont, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QCheckBox, QComboBox, QGroupBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QMessageBox, QFileDialog, QSplitter,
    QTextEdit, QPlainTextEdit, QInputDialog, QScrollArea, QDialogButtonBox,
)

# ======================================================================
# 一、常量与路径
# ======================================================================

# 数值上限（游戏内部为 int32）
MAX_INT = 2100000000
MAX_COUNT = 2100000000

# 存档槽数量（游戏固定 4 个）
SLOT_COUNT = 4

# 默认存档目录（本机实测路径；找不到时由用户在「设置」里指定）
DEFAULT_SAVE_DIR = r"d:\GAME_H\2_Img\大侠狂想曲\大侠狂想曲\大侠狂想曲_Data\Data\Save"
GAME_ROOT = r"d:\GAME_H\2_Img\大侠狂想曲\大侠狂想曲"

# 游戏进程名（用于检测游戏是否在运行 —— 游戏运行时它的存档会自动覆盖我们的修改）
GAME_EXE_NAMES = ("大侠狂想曲.exe", "大侠狂想曲")
# 保存后监视文件是否被外部改写的时长（毫秒）与轮询间隔
SAVE_WATCH_MS = 60000
SAVE_WATCH_INTERVAL = 2000

# 物品实例 property 的零模板（非装备类物品存档里就是这一份全零数据）
ZERO_PROPERTY = {
    "id": 0, "name": "", "keyName": "",
    "minAttack": 0, "maxAttack": 0, "attack": 0,
    "minArmor": 0, "maxArmor": 0, "armor": 0,
    "crit": 0, "critHit": 0, "moveSpeed": 0, "dodge": 0, "maxHP": 0,
}

# 物品大分类显示顺序
ITEM_TYPE_ORDER = [
    ("武器 Weapon", lambda it: it.get("itemTypeShow") == "Weapon"),
    ("护甲 Armor", lambda it: it.get("itemTypeShow") == "Armor"),
    ("饰品 Accessory", lambda it: it.get("itemTypeShow") == "Accessory"),
    ("功法 GongFa", lambda it: it.get("itemTypeShow") == "GongFa"),
    ("心法 XinFa", lambda it: it.get("itemTypeShow") == "XinFa"),
    ("食物 Food", lambda it: it.get("itemTypeShow") == "Food"),
    ("丹药 Medicine", lambda it: it.get("itemTypeShow") == "Medicine"),
    ("种子 Seed", lambda it: it.get("itemTypeShow") == "Seed"),
    ("食材 FoodMaterial", lambda it: it.get("itemTypeShow") == "FoodMaterial"),
    ("材料 Materials", lambda it: it.get("itemTypeShow") in ("Materials", "MedicineMaterials")),
    ("矿物 Mineral", lambda it: it.get("itemTypeShow") == "Mineral"),
    ("书籍 Book", lambda it: it.get("itemTypeShow") in ("BookExperience", "BookPlant")),
    ("菜谱/配方 Recipe", lambda it: it.get("itemTypeShow") == "Recipe"),
    ("图纸 Blueprint", lambda it: it.get("itemTypeShow") == "Blueprint"),
    ("工具 Tools", lambda it: it.get("itemTypeShow") in ("Tools", "PickAxe", "Fishing", "Sprinkler", "Hoe", "Axe", "Sickle")),
    ("建筑 Building", lambda it: it.get("itemTypeShow") == "Building"),
    ("工作台 Workbench", lambda it: it.get("itemTypeShow") == "Workbench"),
    ("饲料 Feed", lambda it: it.get("itemTypeShow") == "Feed"),
    ("礼物 Gift", lambda it: it.get("itemTypeShow") in ("Gift", "GiftPackage")),
    ("包裹 Package", lambda it: it.get("itemTypeShow") == "Package"),
    ("任务物品 TaskItem", lambda it: it.get("itemTypeShow") in ("TaskItem", "Task props")),
    ("其它 Other", lambda it: True),
]

# 任务状态
TASK_STATE_LABELS = {0: "未开始", 1: "进行中", 2: "已完成"}

# 存档槽信息(txt) 的格式说明
SLOT_TXT_NOTE = "第1行=玩家名  第2行=游戏进度摘要  第3行=保存时间"


def app_dir():
    """程序所在目录（打包成 exe 后为 exe 所在目录）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def data_dir():
    return os.path.join(app_dir(), "data")


def settings_path():
    return os.path.join(app_dir(), "设置.json")


def backup_dir():
    d = os.path.join(app_dir(), "backups")
    os.makedirs(d, exist_ok=True)
    return d


def history_path():
    return os.path.join(app_dir(), "历史记录.json")


# ======================================================================
# 二、设置持久化（实时自动保存）
# ======================================================================

DEFAULT_SETTINGS = {
    "save_dir": DEFAULT_SAVE_DIR,
    "last_slot": 0,
    "max_backups": 30,
    "auto_backup_on_save": True,
    "confirm_on_save": True,
    "block_save_when_game_running": True,
    "window_geometry": "",
    "window_maximized": False,
}

_settings_cache = None


def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return dict(_settings_cache)
    st = dict(DEFAULT_SETTINGS)
    try:
        with open(settings_path(), "r", encoding="utf-8") as f:
            st.update(json.load(f))
    except Exception:
        pass
    if not os.path.isdir(st.get("save_dir") or ""):
        found = detect_save_dir()
        if found:
            st["save_dir"] = found
    _settings_cache = st
    return dict(st)


def save_settings(st):
    """原子写入 设置.json（tmp + os.replace）。"""
    global _settings_cache
    _settings_cache = dict(st)
    p = settings_path()
    tmp = p + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=1)
        os.replace(tmp, p)
        return True
    except Exception:
        return False


def _enum_processes():
    """用 Win32 API 枚举进程，返回 [(进程名, pid)]；非 Windows 或失败返回 None。

    注意：**不要用 `tasklist`** —— 本机 tasklist 会卡死（超时也不返回），
    而 CreateToolhelp32Snapshot 扫 294 个进程只要 0.13 秒。
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None
    TH32CS_SNAPPROCESS = 0x00000002
    MAX_PATH = 260

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_void_p),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * MAX_PATH),
        ]

    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        k32.Process32First.argtypes = [ctypes.c_void_p, ctypes.POINTER(PROCESSENTRY32)]
        k32.Process32Next.argtypes = [ctypes.c_void_p, ctypes.POINTER(PROCESSENTRY32)]
        k32.CloseHandle.argtypes = [ctypes.c_void_p]

        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if not snap or snap == ctypes.c_void_p(-1).value:
            return None
        out = []
        try:
            pe = PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
            if k32.Process32First(snap, ctypes.byref(pe)):
                while True:
                    out.append((pe.szExeFile.decode("gbk", "replace"),
                                int(pe.th32ProcessID)))
                    if not k32.Process32Next(snap, ctypes.byref(pe)):
                        break
        finally:
            k32.CloseHandle(ctypes.c_void_p(snap))
        return out
    except Exception:
        return None


def list_process_names():
    """返回进程名列表；非 Windows 或失败返回 None。"""
    procs = _enum_processes()
    return None if procs is None else [p[0] for p in procs]


def _is_game_name(name):
    low = (name or "").lower()
    for t in GAME_EXE_NAMES:
        tl = t.lower()
        if low == tl or low.replace(".exe", "") == tl.replace(".exe", ""):
            return True
        if tl.replace(".exe", "") in low:      # 宽松匹配（带版本后缀等情况）
            return True
    return False


def _process_start_time(pid):
    """取进程启动时间（datetime）；失败返回 None。"""
    try:
        import ctypes
        from ctypes import wintypes

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", wintypes.DWORD),
                        ("dwHighDateTime", wintypes.DWORD)]

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(FILETIME)] * 4
        k32.CloseHandle.argtypes = [ctypes.c_void_p]

        h = k32.OpenProcess(0x1000, False, pid)     # QUERY_LIMITED_INFORMATION
        if not h:
            return None
        try:
            ct, ex, ke, us = FILETIME(), FILETIME(), FILETIME(), FILETIME()
            if not k32.GetProcessTimes(ctypes.c_void_p(h), ctypes.byref(ct),
                                       ctypes.byref(ex), ctypes.byref(ke),
                                       ctypes.byref(us)):
                return None
            v = (ct.dwHighDateTime << 32) | ct.dwLowDateTime
            return datetime(1601, 1, 1) + timedelta(microseconds=v // 10)
        finally:
            k32.CloseHandle(ctypes.c_void_p(h))
    except Exception:
        return None


def _find_game_process():
    """返回 (pid, 启动时间 datetime 或 None)，找不到返回 None。"""
    procs = _enum_processes()
    if procs is None:
        return None
    for name, pid in procs:
        if _is_game_name(name):
            return (pid, _process_start_time(pid))
    return None


def game_process_running():
    """检测游戏进程是否在运行。返回 True / False / None(无法检测)。

    ★ 这是本工具最重要的一条安全前提：游戏运行时它在内存里持有存档数据，
    存档/自动存档/退出时会把内存里的数据写回文件，直接覆盖我们的修改；
    而且游戏在主菜单里已经把存档读进内存后，再点「读档」也不会重新读盘。
    """
    procs = _enum_processes()
    if procs is None:
        return None
    return any(_is_game_name(n) for n, _ in procs)


def human_duration(seconds):
    """把秒数写成「1 天 1 小时 41 分」这样的中文时长。"""
    tot = int(max(0, seconds))
    if tot >= 86400:
        return "%d 天 %d 小时 %d 分" % (tot // 86400, tot % 86400 // 3600,
                                       tot % 3600 // 60)
    if tot >= 3600:
        return "%d 小时 %d 分" % (tot // 3600, tot % 3600 // 60)
    return "%d 分" % (tot // 60)


def game_process_info():
    """返回 (是否运行, pid, 启动时间 datetime|None, 描述文字)。

    描述文字形如「游戏已连续运行 1 天 1 小时 41 分（PID 15956，启动于 09-19 03:59:00）」，
    用来在警示条上直接告诉用户“游戏压根没重启过”。
    """
    found = _find_game_process()
    if found is None:
        if os.name != "nt":
            return (None, None, None, "无法检测游戏进程（非 Windows）")
        return (False, None, None, "未检测到游戏进程")
    pid, st = found
    if st is None:
        return (True, pid, None, "游戏正在运行（PID %d，拿不到启动时间）" % pid)
    dur = human_duration((datetime.now() - st).total_seconds())
    return (True, pid, st,
            "游戏已连续运行 %s（PID %d，启动于 %s）"
            % (dur, pid, st.strftime("%m-%d %H:%M:%S")))


def file_signature(path):
    """(大小, mtime_ns) —— 用于判断文件是否被外部改写。"""
    try:
        st = os.stat(path)
        return (st.st_size, st.st_mtime_ns)
    except Exception:
        return None


def detect_save_dir():
    """自动探测存档目录。"""
    cands = [DEFAULT_SAVE_DIR]
    for root in (r"d:\GAME_H", r"e:\GAME_H", r"c:\GAME_H", "d:\\", "e:\\"):
        if not os.path.isdir(root):
            continue
        try:
            for name in os.listdir(root):
                p = os.path.join(root, name)
                if os.path.isdir(p):
                    cands.append(p)
        except Exception:
            continue
    for c in cands:
        if os.path.isfile(os.path.join(c, "save0player.json")):
            return c
    # 两级深挖常见命名
    for c in cands:
        if not os.path.isdir(c):
            continue
        try:
            for name in os.listdir(c):
                sub = os.path.join(c, name)
                for sub2 in (sub, os.path.join(sub, name + "_Data", "Data", "Save")):
                    if os.path.isfile(os.path.join(sub2, "save0player.json")):
                        return sub2
        except Exception:
            continue
    return ""


# 历史记录（打开过的存档目录）
def load_history():
    try:
        with open(history_path(), "r", encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, list) else []
    except Exception:
        return []


def push_history(path):
    if not path:
        return
    h = [x for x in load_history() if x != path]
    h.insert(0, path)
    try:
        with open(history_path(), "w", encoding="utf-8") as f:
            json.dump(h[:20], f, ensure_ascii=False, indent=1)
    except Exception:
        pass


# ======================================================================
# 三、数据表库加载（startup 一次，带缓存）
# ======================================================================

_LIB_CACHE = {}


def _load_lib(fname, key):
    ck = (fname, key)
    if ck in _LIB_CACHE:
        return _LIB_CACHE[ck]
    p = os.path.join(data_dir(), fname)
    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        val = d.get(key) or []
    except Exception:
        val = []
    _LIB_CACHE[ck] = val
    return val


def item_lib():
    """物品库 [ {id,name,nameKey,...} ]"""
    return _load_lib("物品库.json", "items")


def item_map():
    ck = ("items_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {it["id"]: it for it in item_lib()}
    return _LIB_CACHE[ck]


def prop_lib_map():
    ck = ("props_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {p["id"]: p for p in _load_lib("装备属性库.json", "props")}
    return _LIB_CACHE[ck]


def npc_lib():
    return _load_lib("NPC库.json", "npcs")


def npc_map():
    ck = ("npc_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {n["id"]: n for n in npc_lib()}
    return _LIB_CACHE[ck]


def npc_display_name(npc_id):
    n = npc_map().get(npc_id)
    if not n:
        return "未知NPC(%s)" % npc_id
    cn = (n.get("name") or "").strip()
    key = (n.get("key") or "").strip()
    if cn and key:
        return "%s(%s)" % (cn, key)
    return cn or key or ("NPC%s" % npc_id)


def chapter_lib():
    return _load_lib("章节任务库.json", "chapters")


def chapter_map():
    ck = ("chapter_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {c["id"]: c for c in chapter_lib()}
    return _LIB_CACHE[ck]


def crop_lib():
    return _load_lib("农作库.json", "crops")


def crop_map():
    ck = ("crop_map",)
    if ck not in _LIB_CACHE:
        _LIB_CACHE[ck] = {c["id"]: c for c in crop_lib()}
    return _LIB_CACHE[ck]


def scene_lib():
    return _load_lib("场景库.json", "scenes")


def buff_lib():
    return _load_lib("状态库.json", "buffs")


def item_name(iid):
    it = item_map().get(iid)
    return it["name"] if it else "未知物品(%s)" % iid


def is_gongfa(iid):
    it = item_map().get(iid)
    return bool(it) and it.get("itemTypeShow") in ("GongFa", "XinFa")


def gongfa_items():
    return [it for it in item_lib() if it.get("itemTypeShow") in ("GongFa", "XinFa")]


def recipe_items():
    return [it for it in item_lib() if it.get("itemTypeShow") in ("Recipe", "Blueprint")]


def weapon_items():
    return [it for it in item_lib()
            if it.get("itemTypeShow") in ("Weapon", "Armor", "Accessory")]


# ======================================================================
# 四、存档读写（保证与游戏原格式逐字节兼容）
# ======================================================================

class RawFloat(float):
    """保留原始文本的浮点数。

    游戏（Unity）把 double 写成 17 位有效数字，例如 222.22796630859376，
    而 Python 的 repr 只给最短可还原文本 222.22796630859375。两者二进制值相同，
    但字节不同。本类记住原文本，序列化时原样输出，保证存档逐字节一致。
    """

    __slots__ = ("raw",)

    def __new__(cls, s):
        o = float.__new__(cls, s)
        o.raw = s if isinstance(s, str) else repr(float(s))
        return o

    def __repr__(self):
        return getattr(self, "raw", float.__repr__(self))


def _enc_json(o, out):
    """自定义 JSON 编码器：紧凑分隔符 + 浮点原文保留（与 json.dumps 输出一致）。"""
    if o is None:
        out.append("null")
    elif o is True:
        out.append("true")
    elif o is False:
        out.append("false")
    elif isinstance(o, RawFloat):
        out.append(getattr(o, "raw", None) or float.__repr__(o))
    elif isinstance(o, float):
        out.append(float.__repr__(o))
    elif isinstance(o, int):
        out.append(str(o))
    elif isinstance(o, str):
        out.append(json.dumps(o, ensure_ascii=False))
    elif isinstance(o, dict):
        out.append("{")
        first = True
        for k, v in o.items():
            if not first:
                out.append(",")
            first = False
            out.append(json.dumps(k if isinstance(k, str) else str(k), ensure_ascii=False))
            out.append(":")
            _enc_json(v, out)
        out.append("}")
    elif isinstance(o, (list, tuple)):
        out.append("[")
        for i, v in enumerate(o):
            if i:
                out.append(",")
            _enc_json(v, out)
        out.append("]")
    else:
        raise TypeError("无法序列化的类型: %r" % type(o).__name__)


def dumps_save(doc):
    """按游戏格式序列化：UTF-8、紧凑分隔符、保持键顺序、浮点原文保留。"""
    out = []
    _enc_json(doc, out)
    return "".join(out)


def read_save(path):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8-sig")
    doc = json.loads(text, parse_float=RawFloat)
    if not isinstance(doc, dict):
        raise ValueError("存档根节点不是对象")
    return doc, text


def write_save(path, doc):
    """写入存档。先写临时文件并回读校验，再替换原文件。"""
    text = dumps_save(doc)
    json.loads(text)                      # 自校验
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)
    return len(text)


def slot_player_path(save_dir, slot):
    return os.path.join(save_dir, "save%dplayer.json" % slot)


def slot_txt_path(save_dir, slot):
    return os.path.join(save_dir, "save%d.txt" % slot)


def slot_png_path(save_dir, slot):
    return os.path.join(save_dir, "save%d.png" % slot)


def read_slot_txt(save_dir, slot):
    """读 saveN.txt：返回 (lines, 编码) ；文件不存在返回 (["","",""], "utf-8")。"""
    p = slot_txt_path(save_dir, slot)
    try:
        with open(p, "rb") as f:
            raw = f.read()
        return raw.decode("utf-8").splitlines(), "utf-8"
    except Exception:
        return ["", "", ""], "utf-8"


def write_slot_txt(save_dir, slot, name, line2=None, time_text=None):
    """写回 saveN.txt，保持「UTF-8 + CRLF + 三行」的原始结构。"""
    p = slot_txt_path(save_dir, slot)
    lines, _ = read_slot_txt(save_dir, slot)
    while len(lines) < 3:
        lines.append("")
    if line2 is not None:
        lines[1] = line2
    lines[0] = name
    if time_text is None:
        time_text = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    lines[2] = time_text
    with open(p, "wb") as f:
        f.write(("\r\n".join(lines[:3]) + "\r\n").encode("utf-8"))


def scan_slots(save_dir):
    """扫描存档槽，返回 [{slot,name,money,level,scene,time,size,exists}]。"""
    out = []
    for i in range(SLOT_COUNT):
        p = slot_player_path(save_dir, i)
        info = {"slot": i, "exists": os.path.isfile(p), "path": p,
                "name": "", "money": 0, "level": 0, "scene": "", "time": "",
                "size": 0, "txt2": "", "bags": 0, "kinds": 0}
        if not info["exists"]:
            out.append(info)
            continue
        try:
            info["size"] = os.path.getsize(p)
            doc, _ = read_save(p)
            info["name"] = doc.get("PlayerName", "")
            info["money"] = doc.get("Money", 0)
            info["level"] = doc.get("level", 0)
            info["scene"] = doc.get("PlayerScene", "")
            info["bags"] = len(doc.get("bagitems") or [])
            info["kinds"] = len({e.get("item", {}).get("id")
                                for e in (doc.get("bagitems") or [])})
        except Exception as e:
            info["name"] = "读取失败: %s" % e
        lines, _ = read_slot_txt(save_dir, i)
        if len(lines) > 2:
            info["txt2"] = lines[1]
            info["time"] = lines[2]
        if not info["time"]:
            info["time"] = datetime.fromtimestamp(
                os.path.getmtime(p)).strftime("%Y/%m/%d %H:%M:%S")
        out.append(info)
    return out


def backup_save(path, note=""):
    """把存档复制到 backups/，返回备份文件路径；最多保留 max_backups 份。"""
    st = load_settings()
    keep = int(st.get("max_backups", 30) or 30)
    d = backup_dir()
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(d, "%s_%s%s" % (stem, tag, ext))
    try:
        shutil.copy2(path, dst)
    except Exception:
        return ""
    try:
        files = sorted(f for f in os.listdir(d) if f.lower().endswith(".json"))
        while len(files) > keep:
            os.remove(os.path.join(d, files.pop(0)))
    except Exception:
        pass
    return dst


# ======================================================================
# 五、纯数据操作层（与 GUI 解耦，便于测试）
# ======================================================================

def new_uuid():
    return str(uuid.uuid4())


def make_property_for(item_id):
    """按装备属性表生成一件装备的 property；非装备返回零模板。"""
    p = prop_lib_map().get(item_id)
    if not p:
        return dict(ZERO_PROPERTY)
    out = {"id": p.get("id", item_id), "name": p.get("name", ""),
           "keyName": p.get("keyName", "")}
    for k, v in ZERO_PROPERTY.items():
        if k in ("id", "name", "keyName"):
            continue
        out[k] = p.get(k, 0)
    # 存档中实例会带上「已随机出的」数值：取区间上限作为默认
    if not out.get("attack") and out.get("maxAttack"):
        out["attack"] = out["maxAttack"]
    if not out.get("armor") and out.get("maxArmor"):
        out["armor"] = out["maxArmor"]
    return out


def make_bag_entry(item_id, count=1, template=None):
    """构造一条背包物品记录；template 为已有的同 id 记录时沿用其 item/property。"""
    lib = item_map().get(item_id)
    if lib is None:
        return None
    item = dict(lib)
    if template:
        item = dict(template.get("item") or item)
    prop = dict(template.get("property") or {}) if template else make_property_for(item_id)
    return {
        "uuid": new_uuid(),
        "count": int(count),
        "item": item,
        "entered": True,
        "property": prop,
    }


def bag_add(doc, field, adds):
    """向 bagitems/toolitems 添加物品。

    adds = [(item_id, count)] ；同 id 已有则数量相加，否则新建条目。
    返回 (新增条目数, 叠加条目数, 失败物品名列表)
    """
    lst = doc.setdefault(field, [])
    by_id = {}
    for e in lst:
        try:
            by_id.setdefault(e["item"]["id"], e)
        except Exception:
            continue
    added = stacked = 0
    failed = []
    for iid, cnt in adds:
        cnt = int(cnt)
        if iid not in item_map():
            failed.append("未知物品ID %s" % iid)
            continue
        if iid in by_id:
            by_id[iid]["count"] = min(MAX_COUNT, int(by_id[iid].get("count", 0)) + cnt)
            stacked += 1
        else:
            e = make_bag_entry(iid, cnt)
            lst.append(e)
            by_id[iid] = e
            added += 1
    return added, stacked, failed


def bag_delete(doc, field, indexes):
    """删除背包条目（按索引），返回被删条目的 uuid 列表。"""
    lst = doc.get(field) or []
    uuids = []
    for i in sorted(set(indexes), reverse=True):
        if 0 <= i < len(lst):
            uuids.append(lst[i].get("uuid"))
            del lst[i]
    return uuids


def field_fix_after_delete(doc, removed_uuids):
    """删除物品后清理引用：手持/鱼竿置空、装备列表摘除、出战中无效 id 保留但提示。"""
    fixed = []
    rset = set(u for u in removed_uuids if u)
    for key in ("handerItemuuid", "fishItemuuid"):
        if doc.get(key) in rset:
            doc[key] = ""
            fixed.append(key)
    le = doc.get("list_equipment")
    if isinstance(le, list):
        keep = [u for u in le if u not in rset]
        if len(keep) != len(le):
            doc["list_equipment"] = keep
            fixed.append("list_equipment")
    return fixed


def list_add_ids(doc, key, values):
    """向「纯 id 列表」追加（去重，保持顺序）。返回实际新增个数。"""
    lst = doc.setdefault(key, [])
    n = 0
    for v in values:
        if v not in lst:
            lst.append(v)
            n += 1
    return n


def list_remove_ids(doc, key, values):
    lst = doc.get(key) or []
    vset = set(values)
    keep = [x for x in lst if x not in vset]
    doc[key] = keep
    return len(lst) - len(keep)


def list_add_pairs(doc, key, pairs):
    """向 [{x,y}] 列表追加，x 去重。"""
    lst = doc.setdefault(key, [])
    have = {e.get("x") for e in lst if isinstance(e, dict)}
    n = 0
    for x, y in pairs:
        if x not in have:
            lst.append({"x": x, "y": y})
            have.add(x)
            n += 1
    return n


def list_remove_pairs(doc, key, xs):
    lst = doc.get(key) or []
    xset = set(xs)
    keep = [e for e in lst if e.get("x") not in xset]
    doc[key] = keep
    return len(lst) - len(keep)


def list_add_dicts(doc, key, records, id_key="taskID"):
    """向 [{id_key,...}] 列表追加（按 id_key 去重）。"""
    lst = doc.setdefault(key, [])
    have = {e.get(id_key) for e in lst if isinstance(e, dict)}
    n = 0
    for r in records:
        if r.get(id_key) not in have:
            lst.append(r)
            have.add(r.get(id_key))
            n += 1
    return n


def list_remove_dicts(doc, key, ids, id_key="taskID"):
    lst = doc.get(key) or []
    idset = set(ids)
    keep = [e for e in lst if e.get(id_key) not in idset]
    doc[key] = keep
    return len(lst) - len(keep)


# ---- 背包统计 ----
def bag_summary(doc, field):
    lst = doc.get(field) or []
    kinds = len(lst)
    total = 0
    for e in lst:
        try:
            total += int(e.get("count", 0))
        except Exception:
            pass
    return kinds, total


# ======================================================================
# 六、通用小组件
# ======================================================================

class NumEdit(QSpinBox):
    """统一的整数输入框（上限 MAX_INT）。"""

    def __init__(self, parent=None, minimum=0, maximum=MAX_INT, step=1):
        super().__init__(parent)
        self.setRange(minimum, maximum)
        self.setSingleStep(step)
        self.setGroupSeparatorShown(True)
        self.setKeyboardTracking(False)


def make_table(headers, parent=None, stretch_last=True):
    t = QTableWidget(parent)
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    h = t.horizontalHeader()
    h.setSectionResizeMode(QHeaderView.Interactive)
    if stretch_last:
        h.setStretchLastSection(True)
    return t


def set_row(t, r, values, align_right_from=1):
    for c, v in enumerate(values):
        it = QTableWidgetItem("" if v is None else str(v))
        if c >= align_right_from:
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        t.setItem(r, c, it)


def info(msg, title="提示", parent=None):
    QMessageBox.information(parent, title, msg)


def warn(msg, title="警告", parent=None):
    QMessageBox.warning(parent, title, msg)


def ask(msg, title="确认", parent=None):
    return QMessageBox.question(parent, title, msg,
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) == QMessageBox.Yes


# ======================================================================
# 七、对话框：物品选择 / 设置 / 关于 / 帮助
# ======================================================================

class ItemPickDialog(QDialog):
    """物品选择对话框：分类树 + 搜索 + 多选 + 数量。"""

    def __init__(self, parent=None, title="选择物品", pool=None,
                 existing_ids=None, show_count=True, default_count=1,
                 multi=True, count_label="数量"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(880, 620)
        self._pool = pool if pool is not None else item_lib()
        self._existing = set(existing_ids or ())
        self._multi = multi
        self._show_count = show_count
        self._tree_data = {}          # QTreeWidgetItem -> [item...]
        self.result_ids = []          # [(id, count)]
        self._build(default_count, count_label)

    # ---------- UI ----------
    def _build(self, default_count, count_label):
        root = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("搜索:"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("输入中文名 / 拼音 / 数字ID，支持多个关键字（空格分隔）")
        self.ed_search.textChanged.connect(self._filter)
        row.addWidget(self.ed_search, 1)
        self.chk_group = QCheckBox("按大分类分组")
        self.chk_group.setChecked(True)
        self.chk_group.toggled.connect(self._rebuild)
        row.addWidget(self.chk_group)
        root.addLayout(row)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "ID", "类型", "说明"])
        self.tree.setColumnWidth(0, 260)
        self.tree.setColumnWidth(1, 70)
        self.tree.setColumnWidth(2, 120)
        self.tree.setSelectionMode(
            QAbstractItemView.ExtendedSelection if self._multi
            else QAbstractItemView.SingleSelection)
        self.tree.itemDoubleClicked.connect(lambda *a: self.accept())
        root.addWidget(self.tree, 1)

        self.lbl_stat = QLabel("")
        root.addWidget(self.lbl_stat)

        bot = QHBoxLayout()
        if self._show_count:
            bot.addWidget(QLabel(count_label + ":"))
            self.sp_count = NumEdit(minimum=1, maximum=MAX_COUNT)
            self.sp_count.setValue(int(default_count))
            self.sp_count.setFixedWidth(140)
            bot.addWidget(self.sp_count)
        else:
            self.sp_count = None
        bot.addStretch(1)
        b_all = QPushButton("全选当前列表")
        b_all.clicked.connect(self._select_all)
        bot.addWidget(b_all)
        b_none = QPushButton("清空选择")
        b_none.clicked.connect(self.tree.clearSelection)
        bot.addWidget(b_none)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("确定")
        bb.button(QDialogButtonBox.Cancel).setText("取消")
        bb.accepted.connect(self._on_ok)
        bb.rejected.connect(self.reject)
        bot.addWidget(bb)
        root.addLayout(bot)

        self._rebuild()

    # ---------- 数据 ----------
    def _rebuild(self):
        self.tree.clear()
        self._tree_data.clear()
        pool = list(self._pool)
        if self.chk_group.isChecked():
            used = set()
            for label, pred in ITEM_TYPE_ORDER[:-1]:
                group = [it for it in pool if it["id"] not in used and pred(it)]
                if not group:
                    continue
                used.update(it["id"] for it in group)
                top = QTreeWidgetItem(["%s (%d)" % (label, len(group)), "", "", ""])
                top.setFirstColumnSpanned(True)
                top.setFlags(Qt.ItemIsEnabled)
                self.tree.addTopLevelItem(top)
                self._tree_data[top] = group
                for it in group:
                    self._add_leaf(top, it)
            rest = [it for it in pool if it["id"] not in used]
            if rest:
                top = QTreeWidgetItem(["其它 (%d)" % len(rest), "", "", ""])
                top.setFirstColumnSpanned(True)
                self.tree.addTopLevelItem(top)
                self._tree_data[top] = rest
                for it in rest:
                    self._add_leaf(top, it)
            self.tree.expandAll()
        else:
            for it in pool:
                self._add_leaf(None, it)
        self._filter(self.ed_search.text())

    def _add_leaf(self, parent, it):
        tags = []
        if it["id"] in self._existing:
            tags.append("已有")
        if it.get("sellValue"):
            tags.append("售%d" % it["sellValue"])
        leaf = QTreeWidgetItem([
            it.get("name", ""), str(it.get("id", "")),
            it.get("itemTypeShow", ""), " ".join(tags)])
        leaf.setData(0, Qt.UserRole, it["id"])
        if it["id"] in self._existing:
            leaf.setForeground(0, QBrush(QColor("#888888")))
        if parent is None:
            self.tree.addTopLevelItem(leaf)
        else:
            parent.addChild(leaf)

    def _all_leaves(self):
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                out.append(top.child(j))
        return out

    def _filter(self, text):
        kws = [k for k in re.split(r"[\s,，]+", (text or "").strip()) if k]
        shown = 0
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            top_shown = 0
            for j in range(top.childCount()):
                leaf = top.child(j)
                iid = leaf.data(0, Qt.UserRole)
                it = item_map().get(iid) or {}
                blob = "%s %s %s %s" % (it.get("name", ""), it.get("nameKey", ""),
                                        it.get("id", ""), it.get("itemTypeShow", ""))
                ok = all(k.lower() in blob.lower() for k in kws)
                leaf.setHidden(not ok)
                if ok:
                    top_shown += 1
            if top.childCount():
                top.setHidden(top_shown == 0)
            shown += top_shown
        self.lbl_stat.setText("共 %d 项（当前显示 %d 项）· 已选中 %d 项"
                              % (len(self._pool), shown, len(self._selected_ids())))

    def _selected_ids(self):
        return [x.data(0, Qt.UserRole) for x in self.tree.selectedItems()
                if x.data(0, Qt.UserRole) is not None]

    def _select_all(self):
        self.tree.blockSignals(True)
        for leaf in self._all_leaves():
            if not leaf.isHidden():
                leaf.setSelected(True)
        self.tree.blockSignals(False)
        self._filter(self.ed_search.text())

    def _on_ok(self):
        ids = self._selected_ids()
        if not ids:
            warn("请先选择至少一个物品。", parent=self)
            return
        cnt = self.sp_count.value() if self.sp_count else 1
        self.result_ids = [(i, cnt) for i in ids]
        self.accept()


class SettingsDialog(QDialog):
    """设置对话框：改动即时保存（无「保存」按钮，只有「关闭」）。"""

    def __init__(self, parent, values, on_change=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(620, 320)
        self._values = dict(values)
        self._on_change = on_change
        self._build()

    def _build(self):
        root = QVBoxLayout(self)

        g1 = QGroupBox("存档目录")
        v1 = QVBoxLayout(g1)
        row = QHBoxLayout()
        self.ed_dir = QLineEdit(self._values.get("save_dir", ""))
        self.ed_dir.setReadOnly(True)
        row.addWidget(self.ed_dir, 1)
        b = QPushButton("浏览…")
        b.clicked.connect(self._browse)
        row.addWidget(b)
        b2 = QPushButton("自动探测")
        b2.clicked.connect(self._auto)
        row.addWidget(b2)
        v1.addLayout(row)
        lb = QLabel("存档文件位于游戏目录：<游戏>\\<游戏>_Data\\Data\\Save\\saveNplayer.json")
        lb.setStyleSheet("color:#666;")
        v1.addWidget(lb)
        root.addWidget(g1)

        g2 = QGroupBox("行为")
        f = QFormLayout(g2)
        self.sp_backup = NumEdit(minimum=1, maximum=999)
        self.sp_backup.setValue(int(self._values.get("max_backups", 30)))
        f.addRow("备份保留份数:", self.sp_backup)
        self.chk_auto_backup = QCheckBox("保存前自动备份（推荐）")
        self.chk_auto_backup.setChecked(bool(self._values.get("auto_backup_on_save", True)))
        f.addRow("", self.chk_auto_backup)
        self.chk_confirm = QCheckBox("保存前弹出确认")
        self.chk_confirm.setChecked(bool(self._values.get("confirm_on_save", True)))
        f.addRow("", self.chk_confirm)
        self.chk_block = QCheckBox("游戏运行时禁止保存（强烈建议保持开启）")
        self.chk_block.setChecked(
            bool(self._values.get("block_save_when_game_running", True)))
        self.chk_block.setToolTip(
            "游戏运行时会把它内存里的存档写回文件，你改的东西会被覆盖，\n"
            "游戏里也看不到任何变化。开启本项后，保存会被直接拒绝。\n"
            "（真实平台上 大侠狂想曲.exe 退干净后才会放行）")
        f.addRow("", self.chk_block)
        root.addWidget(g2)

        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.button(QDialogButtonBox.Close).setText("关闭")
        bb.rejected.connect(self.accept)
        bb.clicked.connect(lambda *a: self.accept())
        root.addWidget(bb)

        # 先 setChecked/setValue 再接信号，避免构造时误触发保存
        self.sp_backup.valueChanged.connect(
            lambda v: self._emit("max_backups", int(v)))
        self.chk_auto_backup.toggled.connect(
            lambda v: self._emit("auto_backup_on_save", bool(v)))
        self.chk_confirm.toggled.connect(
            lambda v: self._emit("confirm_on_save", bool(v)))
        self.chk_block.toggled.connect(
            lambda v: self._emit("block_save_when_game_running", bool(v)))

    def _emit(self, key, val):
        self._values[key] = val
        if self._on_change:
            self._on_change(key, val)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "选择存档目录",
                                             self._values.get("save_dir") or "")
        if d:
            self.ed_dir.setText(d)
            self._emit("save_dir", d)

    def _auto(self):
        d = detect_save_dir()
        if not d:
            warn("未能自动找到存档目录，请手动浏览选择。", parent=self)
            return
        self.ed_dir.setText(d)
        self._emit("save_dir", d)
        info("已找到存档目录：\n%s" % d, parent=self)

    def result_values(self):
        return dict(self._values)


HELP_TEXT = """
<h2>大侠狂想曲 存档修改器 v%s</h2>
<p>本工具直接读写游戏的 <b>saveNplayer.json</b>（Unity JSON 存档），
并同步维护同名的 <b>saveN.txt</b>（玩家名/进度摘要/保存时间）。</p>

<h3>一、使用步骤</h3>
<ol>
<li>在左侧选择存档槽（1~4），或点工具栏「打开存档…」选择 json 文件。</li>
<li>在右侧各页签中修改；所有改动只存在内存里，标题栏出现 <b>*</b> 表示未保存。</li>
<li>点「保存」（Ctrl+S）写回原文件；首次保存会自动备份到程序目录 backups\\。</li>
<li>想撤销全部修改：点「重新载入」（Ctrl+R）。</li>
</ol>

<h3>二、页签说明</h3>
<ul>
<li><b>基础属性</b>：姓名、金钱、经验、熟练度、等级、HP/MP、疲劳、游戏时间等，
并提供一键最大值。</li>
<li><b>背包</b>：bagitems 全部条目；可添加（从 176 种物品库中选）、删除、改数量、
改装备属性；工具栏 toolitems 单独一区。</li>
<li><b>武学/配方</b>：已学武学(list_skill)、出招栏(list_skillRun 6 格)、已学配方(list_recipe)。</li>
<li><b>NPC/剧情</b>：NPC 好感度、已触发对话(activeDialogues)、送礼/对话记录、点击事件计数。</li>
<li><b>任务</b>：taskinfos，可改状态（未开始/进行中/已完成）。</li>
<li><b>农场/建造</b>：farmitems 农田作物与 list_buildinfos 建筑。</li>
<li><b>世界/杂项</b>：当前场景与坐标、已激活场景、制作队列、标记、Perk/装备栏等。</li>
<li><b>高级</b>：整份 JSON 文本编辑（慎用）、备份管理、存档格式校验。</li>
</ul>

<h3>三、安全提示（★ 必读：为什么“改了游戏里没变化”）</h3>
<ul>
<li>保存前会自动备份（可在「设置」里关闭）；备份目录：程序目录 <b>backups\\</b>。</li>
<li><b>必须先完全退出游戏，再改存档，最后才启动游戏读档。</b><br>
原因是 Unity 游戏只在自己启动/读档时读一次盘：<br>
① 游戏运行中在游戏里点「读档」<b>不会重新读文件</b>，所以你改了也看不到；<br>
② 游戏一旦在游戏内存档，就把内存里的旧数据整份写回文件，<b>直接覆盖</b>你的修改。<br>
所以“改了没效果”几乎都是<b>游戏进程一直没退出</b>（程序顶部红色横幅会显示它已连续运行多久）。</li>
<li>程序会检测游戏进程：运行中保存会被<b>直接拒绝</b>并弹窗说明，防止你白改一场。
如确需强制写入，可在「设置…」里关闭「游戏运行时禁止保存」。</li>
<li>保存后程序会回读校验（弹窗显示文件里实际有多少条物品），并在之后 60 秒内监视
文件是否被外部进程改写，一旦发现立刻报警。</li>
<li>数值上限为 2,100,000,000（int32 安全范围），超出会被拒绝。</li>
<li>删除物品时，如果该物品正被手持/装备，程序会自动清理引用。</li>
</ul>

<h3>四、数据来源</h3>
<p>物品库、装备属性、配方、农作物、NPC、章节任务等表来自游戏
<code>resources.assets</code> 内的 JSON 文本资产（开发时一次性提取，见 _scaffold\\）。</p>
""" % __version__


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.resize(760, 640)
        v = QVBoxLayout(self)
        t = QTextEdit()
        t.setReadOnly(True)
        t.setHtml(HELP_TEXT)
        v.addWidget(t)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.button(QDialogButtonBox.Close).setText("关闭")
        bb.rejected.connect(self.accept)
        bb.clicked.connect(lambda *a: self.accept())
        v.addWidget(bb)


# ======================================================================
# 八、主窗口
# ======================================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " v" + __version__)
        self.resize(1440, 900)

        self.st = load_settings()
        self.save_dir = self.st.get("save_dir") or DEFAULT_SAVE_DIR
        self.slot = int(self.st.get("last_slot", 0) or 0)
        self.path = ""            # 当前存档 json 全路径
        self.doc = {}             # 当前存档数据
        self.orig_text = ""       # 载入时原始文本
        self.dirty = False
        self._loading = False     # True 表示正在批量刷新控件，屏蔽信号

        # 设置实时保存（800ms 防抖）
        self._settings_timer = QTimer(self)
        self._settings_timer.setSingleShot(True)
        self._settings_timer.setInterval(800)
        self._settings_timer.timeout.connect(self._save_settings_now)

        self._build_toolbar()
        self._build_central()
        self._restore_geometry()
        self.refresh_slots()
        self._guard(self.refresh_all)      # 先刷一遍（空档时各表显示 0）
        self._select_start_slot()

        # 游戏进程检测（每 10 秒重新查一次）
        self._proc_timer = QTimer(self)
        self._proc_timer.setInterval(10000)
        self._proc_timer.timeout.connect(self._check_game_process)
        self._proc_timer.start()
        self._check_game_process(notify=True)

        # 保存后「文件是否被外部改写」的监视
        self._watch_timer = QTimer(self)
        self._watch_timer.setInterval(SAVE_WATCH_INTERVAL)
        self._watch_timer.timeout.connect(self._on_watch_tick)
        self._watch_deadline = None
        self._watch_sig = None
        self._watch_path = ""

    # ------------------------------------------------------------------
    # 游戏进程检测 / 存档被覆盖监视（★ 核心安全机制）
    # ------------------------------------------------------------------
    def _check_game_process(self, notify=False):
        """检查游戏是否在运行，更新顶部警示条。"""
        running, pid, st, desc = game_process_info()
        if running:
            if st is not None:
                head = ("⚠ 游戏正在运行，且已连续运行 %s（PID %s）——现在改＝白改！"
                        "请先完全退出游戏（点击重新检测）"
                        % (human_duration((datetime.now() - st).total_seconds()), pid))
            else:
                head = ("⚠ 游戏正在运行（PID %s）——现在改＝白改！"
                        "请先完全退出游戏（点击重新检测）" % pid)
            self.lbl_game_warn.setText(head)
            self.lbl_game_warn.setVisible(True)
            self.lbl_game_warn.setToolTip(
                "%s\n\n" % desc +
                "游戏运行时：\n"
                "· 它会把内存里的存档写回文件，直接覆盖你的修改；\n"
                "· 它不会重新读盘，所以你在游戏里怎么「读档」都看不到改动。\n\n"
                "正确做法：完全退出游戏 → 用本工具修改并保存 → 重新启动游戏 → 读档。")
            if notify:
                QMessageBox.warning(
                    self, "检测到游戏正在运行",
                    "%s\n\n"
                    "你做的任何修改（加道具 / 删道具 / 改数值）都【不会生效】：\n"
                    "· 游戏不会重新读盘，游戏里看永远是原来那样；\n"
                    "· 游戏稍后一存档，就会把它内存里的旧数据写回文件，覆盖你的修改。\n\n"
                    "请先【完全退出游戏】（任务管理器里确认 大侠狂想曲.exe 已结束），\n"
                    "等程序顶部的红色提示消失后，再修改并保存。" % desc)
        else:
            if self.lbl_game_warn.isVisible():
                self.lbl_game_warn.setVisible(False)
        return running

    def _start_save_watch(self, path):
        """保存后开始监视：若文件被外部进程改写，提示用户。"""
        self._watch_path = path
        self._watch_sig = file_signature(path)
        self._watch_deadline = datetime.now().timestamp() + SAVE_WATCH_MS / 1000.0
        self._watch_timer.start()

    def _on_watch_tick(self):
        if self._watch_deadline is None or \
                datetime.now().timestamp() > self._watch_deadline:
            self._watch_timer.stop()
            self._watch_deadline = None
            return
        sig = file_signature(self._watch_path)
        if sig is not None and self._watch_sig is not None and sig != self._watch_sig:
            self._watch_timer.stop()
            self._watch_deadline = None
            self.lbl_game_warn.setText(
                "⚠ 存档刚被外部改写！游戏可能正在运行（点击重新检测）")
            self.lbl_game_warn.setVisible(True)
            QMessageBox.warning(
                self, "存档被外部改写",
                "刚刚保存的存档已经被其它程序改写了：\n%s\n\n"
                "几乎可以肯定是【游戏正在运行并把自己的存档写了回去】，\n"
                "这意味着你刚才的修改已经丢失。\n\n"
                "请：\n"
                "1. 完全退出游戏（任务管理器确认 大侠狂想曲.exe 已结束）\n"
                "2. 重新用本工具修改并保存\n"
                "3. 再启动游戏读档" % self._watch_path)
            self.mark_dirty()
            self.refresh_slots()

    # ------------------------------------------------------------------
    # 界面
    # ------------------------------------------------------------------
    def _act(self, toolbar, text, tip, slot, shortcut=None):
        a = QAction(text, self)
        a.setToolTip(tip + ((" (%s)" % shortcut) if shortcut else ""))
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        toolbar.addAction(a)
        return a

    def _build_toolbar(self):
        tb = self.addToolBar("主工具栏")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))

        self.status_dot = QLabel()
        self.status_dot.setFixedSize(12, 12)
        self._set_dot("#9e9e9e", "未打开存档")
        tb.addWidget(self.status_dot)

        self._act(tb, "打开存档…", "手动选择 saveNplayer.json", self.on_open_file, "Ctrl+O")
        self._act(tb, "重新载入", "放弃所有未保存的修改，重新从磁盘读取", self.on_reload, "Ctrl+R")
        tb.addSeparator()
        self._act(tb, "保存", "写回存档文件", self.on_save, "Ctrl+S")
        self._act(tb, "另存为…", "保存到其它文件", self.on_save_as, "Ctrl+Shift+S")
        self._act(tb, "备份当前", "把当前存档复制到 backups\\ 目录", self.on_backup_now)
        tb.addSeparator()
        self._act(tb, "刷新列表", "重新扫描存档槽", self.refresh_slots)
        tb.addSeparator()
        self._act(tb, "设置…", "存档目录与行为设置", self.open_settings)
        self._act(tb, "使用说明", "打开帮助文档", self.show_help)
        self._act(tb, "关于", "版本信息", self.show_about)

        self.lbl_path = QLabel("（未打开存档）")
        self.lbl_path.setStyleSheet("color:#666; padding-left:8px;")
        tb.addWidget(self.lbl_path)

        # ★ 游戏正在运行时的醒目警示（点击可重新检测）
        self.lbl_game_warn = QLabel("")
        self.lbl_game_warn.setStyleSheet(
            "background:#c62828; color:white; font-weight:bold; padding:2px 8px;"
            "margin-left:8px; border-radius:3px;")
        self.lbl_game_warn.setCursor(Qt.PointingHandCursor)
        self.lbl_game_warn.setVisible(False)
        self.lbl_game_warn.mousePressEvent = lambda ev: self._check_game_process(True)
        tb.addWidget(self.lbl_game_warn)

    def _build_central(self):
        sp = QSplitter(Qt.Horizontal)
        self.setCentralWidget(sp)

        # ---- 左侧：存档槽 ----
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(6, 6, 3, 6)
        lv.addWidget(QLabel("存档槽（1~4）"))
        self.list_slots = QListWidget()
        self.list_slots.setWordWrap(True)
        self.list_slots.currentRowChanged.connect(self.on_slot_changed)
        lv.addWidget(self.list_slots, 1)

        gb = QGroupBox("存档预览")
        gv = QVBoxLayout(gb)
        self.lbl_preview = QLabel("（无截图）")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setMinimumHeight(150)
        self.lbl_preview.setStyleSheet("background:#222; color:#aaa;")
        gv.addWidget(self.lbl_preview)
        self.lbl_slot_info = QLabel("")
        self.lbl_slot_info.setWordWrap(True)
        self.lbl_slot_info.setStyleSheet("color:#555;")
        gv.addWidget(self.lbl_slot_info)
        lv.addWidget(gb)
        sp.addWidget(left)

        # ---- 右侧：页签 ----
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_basic_tab(), "基础属性")
        self.tabs.addTab(self.create_bag_tab(), "背包 / 工具栏")
        self.tabs.addTab(self.create_skill_tab(), "武学 / 配方")
        self.tabs.addTab(self.create_npc_tab(), "NPC / 剧情")
        self.tabs.addTab(self.create_task_tab(), "任务")
        self.tabs.addTab(self.create_farm_tab(), "农场 / 建造")
        self.tabs.addTab(self.create_world_tab(), "世界 / 杂项")
        self.tabs.addTab(self.create_adv_tab(), "高级")
        sp.addWidget(self.tabs)
        sp.setStretchFactor(0, 0)
        sp.setStretchFactor(1, 1)
        sp.setSizes([300, 1140])

        self.statusBar().showMessage("就绪")

    def _set_dot(self, color, tip):
        self.status_dot.setStyleSheet(
            "background:%s; border-radius:6px;" % color)
        self.status_dot.setToolTip(tip)

    def _restore_geometry(self):
        geo = self.st.get("window_geometry") or ""
        try:
            import base64
            if geo:
                self.restoreGeometry(base64.b64decode(geo.encode("ascii")))
        except Exception:
            pass
        if self.st.get("window_maximized"):
            self.showMaximized()

    # ------------------------------------------------------------------
    # 存档槽
    # ------------------------------------------------------------------
    def refresh_slots(self, reselect=True):
        """只重扫并重画存档槽列表。

        ★ 本方法**绝不能重新读盘**：它会被「设置」「保存」「监视」等多处调用，
        一旦触发 `on_slot_changed → open_slot → load_file`，
        就会把用户还没保存的修改惄惄冲掉。因此选行时也必须屏蔽信号。
        """
        self.save_dir = self.st.get("save_dir") or DEFAULT_SAVE_DIR
        self._slots = scan_slots(self.save_dir)
        self.list_slots.blockSignals(True)
        try:
            self.list_slots.clear()
            for s in self._slots:
                if s["exists"]:
                    txt = "槽%d  %s\n  ¥%s  Lv%s  %s\n  物品 %d 条/%d 种 · %s" % (
                        s["slot"] + 1, s["name"] or "?", "{:,}".format(s["money"]),
                        s["level"], s["scene"], s.get("bags", 0), s.get("kinds", 0),
                        s["time"])
                else:
                    txt = "槽%d  （空存档）" % (s["slot"] + 1)
                it = QListWidgetItem(txt)
                it.setData(Qt.UserRole, s["slot"])
                self.list_slots.addItem(it)
            if reselect:
                row = min(max(self.slot, 0), self.list_slots.count() - 1)
                self.list_slots.setCurrentRow(row)      # 信号已屏蔽，不会触发读盘
        finally:
            self.list_slots.blockSignals(False)

    def _sync_slot_selection(self):
        """把左侧高亮挪回当前真正载入的槽（不触发信号）。"""
        changed = self.list_slots.blockSignals(True)
        try:
            self.list_slots.setCurrentRow(min(max(self.slot, 0),
                                             self.list_slots.count() - 1))
        finally:
            self.list_slots.blockSignals(changed)

    def _select_start_slot(self):
        row = min(max(self.slot, 0), self.list_slots.count() - 1)
        if row >= 0:
            changed = self.list_slots.blockSignals(True)
            try:
                self.list_slots.setCurrentRow(row)
            finally:
                self.list_slots.blockSignals(changed)
            self.open_slot(row, confirm=False)

    def on_slot_changed(self, row):
        if row < 0:
            return
        self.open_slot(row, confirm=True)

    def open_slot(self, slot, confirm=True):
        p = slot_player_path(self.save_dir, slot)
        if not os.path.isfile(p):
            self._show_slot_info(slot)
            return
        if p == self.path:
            # 已经是当前正在编辑的存档 —— 不要重新读盘（会冲掉未保存的修改）
            self._show_slot_info(slot)
            return
        if confirm and self.dirty:
            if not ask("当前存档有未保存的修改，确定放弃并打开「槽%d」？" % (slot + 1), parent=self):
                self._sync_slot_selection()    # 高亮挪回原槽
                return
        self.load_file(p)
        self.slot = slot
        self._settings_timer_set("last_slot", slot)
        self._show_slot_info(slot)

    def _show_slot_info(self, slot):
        s = next((x for x in getattr(self, "_slots", []) if x["slot"] == slot), None)
        png = slot_png_path(self.save_dir, slot)
        if os.path.isfile(png):
            pm = QPixmap(png)
            if not pm.isNull():
                self.lbl_preview.setPixmap(
                    pm.scaled(self.lbl_preview.width() or 280, 200,
                              Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.lbl_preview.setStyleSheet("background:#222;")
            else:
                self._no_preview()
        else:
            self._no_preview()
        if s and s["exists"]:
            kb = s["size"] / 1024.0
            self.lbl_slot_info.setText(
                "槽%d  |  %.1f KB\n物品: %d 条 / %d 种\n进度摘要: %s\n保存时间: %s\n文件: %s"
                % (slot + 1, kb, s.get("bags", 0), s.get("kinds", 0),
                   s["txt2"] or "?", s["time"], os.path.basename(s["path"])))
        else:
            self.lbl_slot_info.setText("槽%d  |  空存档（无 save%dplayer.json）"
                                       % (slot + 1, slot))

    def _no_preview(self):
        self.lbl_preview.setText("（无截图）")
        self.lbl_preview.setStyleSheet("background:#222; color:#aaa;")

    # ------------------------------------------------------------------
    # 打开 / 保存
    # ------------------------------------------------------------------
    def on_open_file(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "打开存档文件", self.save_dir or "", "存档 JSON (*player.json *.json)")
        if p:
            self.load_file(p)
            push_history(os.path.dirname(p))

    def load_file(self, path):
        try:
            doc, text = read_save(path)
        except Exception as e:
            warn("读取存档失败：\n%s" % e, parent=self)
            return False
        self.doc = doc
        self.orig_text = text
        self.path = path
        self.dirty = False
        self.lbl_path.setText(path)
        m = re.match(r"^save(\d+)player\.json$", os.path.basename(path))
        if m:
            self.slot = int(m.group(1))
        self._loading = True
        try:
            self.refresh_all()
        finally:
            self._loading = False
        self._update_title()
        self.statusBar().showMessage("已载入 %s（%d 字节）" % (os.path.basename(path), len(text)))
        return True

    def _update_title(self):
        star = " *" if self.dirty else ""
        base = APP_NAME + " v" + __version__
        name = os.path.basename(self.path) if self.path else "未打开存档"
        self.setWindowTitle("%s%s — %s" % (base, star, name))
        self._set_dot("#e53935" if self.dirty else ("#2e7d32" if self.path else "#9e9e9e"),
                      "未保存" if self.dirty else ("已保存" if self.path else "未打开存档"))

    def mark_dirty(self):
        if self._loading:
            return
        if not self.dirty:
            self.dirty = True
        self._update_title()

    def _txt_path_for(self, path):
        d, b = os.path.split(path)
        m = re.match(r"^(save\d+)player\.json$", b)
        if not m:
            return None
        return os.path.join(d, m.group(1) + ".txt")

    def on_save(self):
        if not self.path:
            self.on_save_as()
            return
        if not self.doc:
            warn("没有可保存的内容。", parent=self)
            return
        # ★ 游戏运行时保存 = 白改（游戏稍后会把内存里的数据写回文件覆盖它）
        st = load_settings()
        if game_process_running():
            self._check_game_process()
            _run, _pid, _st, _desc = game_process_info()
            if st.get("block_save_when_game_running", True):
                QMessageBox.critical(
                    self, "已拒绝保存：游戏正在运行",
                    "%s\n\n"
                    "已【拒绝写入】。原因：\n"
                    "· 游戏不会重新读盘 —— 你在游戏里怎么读档都看不到改动；\n"
                    "· 游戏存档时会把内存里的旧数据写回文件，把你的修改直接覆盖掉。\n\n"
                    "请先完全退出游戏（任务管理器确认 大侠狂想曲.exe 已结束），\n"
                    "程序顶部的红色提示消失后再保存。\n\n"
                    "（如确需强制写入，可在「设置…」里关闭「游戏运行时禁止保存」）" % _desc)
                return
            if not ask(
                    "%s\n\n"
                    "游戏运行时保存基本等于白改（游戏稍后会把内存里的数据写回文件）。\n\n"
                    "仍要继续写入吗？" % _desc,
                    title="游戏正在运行", parent=self):
                return
        if st.get("confirm_on_save", True):
            if not ask("确定写回存档文件？\n%s" % self.path, parent=self):
                return
        if st.get("auto_backup_on_save", True):
            b = backup_save(self.path)
            if b:
                self.statusBar().showMessage("已备份到 %s" % os.path.basename(b), 5000)
        n_bag = len(self.doc.get("bagitems") or [])
        try:
            write_save(self.path, self.doc)
        except Exception as e:
            warn("保存失败：\n%s" % e, parent=self)
            return
        # ★ 回读校验：确认真的写进去了（避免“以为存了”）
        try:
            chk, _txt = read_save(self.path)
            n_bag2 = len(chk.get("bagitems") or [])
            verified = (n_bag2 == n_bag)
        except Exception as e:
            verified = False
            n_bag2 = -1
        # 同步 saveN.txt（玩家名 + 保存时间），第 2 行进度摘要保持原样
        tp = self._txt_path_for(self.path)
        if tp and os.path.isfile(tp):
            try:
                write_slot_txt(os.path.dirname(self.path),
                               int(re.match(r"^save(\d+)player\.json$",
                                            os.path.basename(self.path)).group(1)),
                               self.doc.get("PlayerName", ""))
            except Exception as e:
                self.statusBar().showMessage("存档已写回，但 txt 同步失败: %s" % e, 8000)
        self.dirty = False
        self._update_title()
        self.refresh_slots()
        # 保存后监视 60 秒：若文件被外部改写（游戏在跑）立刻提醒
        self._start_save_watch(self.path)
        try:
            self.orig_text = dumps_save(self.doc)
        except Exception:
            pass
        msg = ["保存成功！", self.path, ""]
        msg.append("回读校验：文件里物品 %d 条（应为 %d 条）%s"
                   % (n_bag2, n_bag, "✔" if verified else "✘ 不一致，请检查！"))
        msg.append("")
        msg.append("下一步：")
        msg.append("1. 完全退出游戏（任务管理器确认 大侠狂想曲.exe 已结束）")
        msg.append("2. 再启动游戏 → 读档 → 检查物品是否出现")
        msg.append("")
        msg.append("⚠ 如果游戏没退出就保存，改动会被游戏覆盖、游戏里也看不到。")
        info("\n".join(msg), parent=self)

    def on_save_as(self):
        if not self.doc:
            warn("没有可保存的内容。", parent=self)
            return
        p, _ = QFileDialog.getSaveFileName(
            self, "另存为", self.path or os.path.join(self.save_dir, "save0player.json"),
            "存档 JSON (*player.json *.json)")
        if not p:
            return
        try:
            write_save(p, self.doc)
        except Exception as e:
            warn("保存失败：\n%s" % e, parent=self)
            return
        self.path = p
        self.lbl_path.setText(p)
        self.dirty = False
        self._update_title()
        info("已另存为：\n%s" % p, parent=self)

    def on_reload(self):
        if not self.path:
            return
        if self.dirty and not ask("放弃所有未保存的修改并重新载入？", parent=self):
            return
        self.load_file(self.path)

    def on_backup_now(self):
        if not self.path or not os.path.isfile(self.path):
            warn("请先打开一个存档。", parent=self)
            return
        b = backup_save(self.path)
        if b:
            info("已备份到：\n%s" % b, parent=self)
        else:
            warn("备份失败。", parent=self)

    # ------------------------------------------------------------------
    # 设置
    # ------------------------------------------------------------------
    def _settings_timer_set(self, key, val):
        self.st[key] = val
        self._settings_timer.start()

    def _save_settings_now(self):
        try:
            import base64
            self.st["window_geometry"] = base64.b64encode(
                bytes(self.saveGeometry())).decode("ascii")
            self.st["window_maximized"] = self.isMaximized()
        except Exception:
            pass
        save_settings(self.st)

    def open_settings(self):
        dlg = SettingsDialog(self, self.st, on_change=self._on_setting_changed)
        dlg.exec()
        self.save_dir = self.st.get("save_dir") or DEFAULT_SAVE_DIR
        self.refresh_slots()

    def _on_setting_changed(self, key, value):
        self.st[key] = value
        if key == "save_dir":
            self.save_dir = value
            self.refresh_slots(reselect=False)
        save_settings(self.st)
        self.statusBar().showMessage("设置已保存：%s" % key, 3000)

    # ------------------------------------------------------------------
    # 帮助
    # ------------------------------------------------------------------
    def show_help(self):
        HelpDialog(self).exec()

    def show_about(self):
        from PySide6 import __version__ as pv
        info("<h3>%s v%s</h3>"
             "<p>游戏：大侠狂想曲（Unity）</p>"
             "<p>存档格式：saveNplayer.json（紧凑 JSON，UTF-8 无 BOM）</p>"
             "<p>Python %s · PySide6 %s</p>"
             "<p>数据表来自游戏 resources.assets 内嵌 JSON。</p>"
             % (APP_NAME, __version__, sys.version.split()[0], pv),
             title="关于", parent=self)

    def closeEvent(self, e):
        self._settings_timer.stop()
        if self.dirty:
            r = QMessageBox.question(
                self, "未保存", "当前存档有未保存的修改，要保存吗？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save)
            if r == QMessageBox.Cancel:
                e.ignore()
                return
            if r == QMessageBox.Save:
                self.on_save()
        self._save_settings_now()
        e.accept()

    # ==================================================================
    # 通用工具
    # ==================================================================
    def _doc_get(self, path, default=None):
        cur = self.doc
        for k in path:
            if isinstance(cur, dict):
                cur = cur.get(k)
            elif isinstance(cur, list) and isinstance(k, int) and 0 <= k < len(cur):
                cur = cur[k]
            else:
                return default
            if cur is None:
                return default
        return cur

    def _doc_set(self, path, val):
        if not self.doc:
            return
        cur = self.doc
        for k in path[:-1]:
            if isinstance(cur, dict):
                if not isinstance(cur.get(k), (dict, list)):
                    cur[k] = {}
                cur = cur[k]
            elif isinstance(cur, list):
                cur = cur[k]
            else:
                return
        if isinstance(cur, dict):
            cur[path[-1]] = val
        elif isinstance(cur, list) and isinstance(path[-1], int):
            while len(cur) <= path[-1]:
                cur.append(0)
            cur[path[-1]] = val

    def _guard(self, fn, *a, **k):
        old = self._loading
        self._loading = True
        try:
            return fn(*a, **k)
        finally:
            self._loading = old

    def _bind_int(self, w, path):
        def on_change(v):
            if self._loading:
                return
            self._doc_set(path, int(v))
            self.mark_dirty()
        w.valueChanged.connect(on_change)

    def _bind_float(self, w, path):
        def on_change(v):
            if self._loading:
                return
            self._doc_set(path, float(v))
            self.mark_dirty()
        w.valueChanged.connect(on_change)

    def _bind_bool(self, w, path):
        def on_change(v):
            if self._loading:
                return
            self._doc_set(path, bool(v))
            self.mark_dirty()
        w.toggled.connect(on_change)

    def _bind_text(self, w, path):
        def on_done():
            if self._loading:
                return
            self._doc_set(path, w.text())
            self.mark_dirty()
        w.editingFinished.connect(on_done)

    def _scroll_page(self):
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        w = QWidget()
        v = QVBoxLayout(w)
        sa.setWidget(w)
        return sa, v

    def _need_doc(self):
        if not self.doc:
            warn("请先打开一个存档。", parent=self)
            return False
        return True

    # ==================================================================
    # 页签 1：基础属性
    # ==================================================================
    def _basic_role_page(self):
        page, v = self._scroll_page()

        # --- 角色 ---
        g = QGroupBox("角色")
        grid = QGridLayout(g)
        self.ed_name = QLineEdit()
        self.ed_name.setMaxLength(24)
        self._bind_text(self.ed_name, ("PlayerName",))
        grid.addWidget(QLabel("姓名:"), 0, 0)
        grid.addWidget(self.ed_name, 0, 1)

        self.sp_money = NumEdit()
        self._bind_int(self.sp_money, ("Money",))
        grid.addWidget(QLabel("金钱:"), 0, 2)
        grid.addWidget(self.sp_money, 0, 3)

        self.sp_exp = NumEdit()
        self._bind_int(self.sp_exp, ("Experience",))
        grid.addWidget(QLabel("经验:"), 0, 4)
        grid.addWidget(self.sp_exp, 0, 5)

        self.sp_prof = NumEdit()
        self._bind_int(self.sp_prof, ("Proficiency",))
        grid.addWidget(QLabel("熟练度:"), 1, 0)
        grid.addWidget(self.sp_prof, 1, 1)

        self.sp_level = NumEdit(maximum=9999)
        self._bind_int(self.sp_level, ("level",))
        grid.addWidget(QLabel("等级:"), 1, 2)
        grid.addWidget(self.sp_level, 1, 3)

        self.sp_farmlevel = NumEdit(maximum=9999)
        self._bind_int(self.sp_farmlevel, ("farmLevel",))
        grid.addWidget(QLabel("农场等级:"), 1, 4)
        grid.addWidget(self.sp_farmlevel, 1, 5)
        v.addWidget(g)

        # --- 状态 ---
        g = QGroupBox("状态")
        grid = QGridLayout(g)
        self.sp_hp = NumEdit()
        self._bind_int(self.sp_hp, ("currentHP",))
        self.sp_mp = NumEdit()
        self._bind_int(self.sp_mp, ("currentMP",))
        self.sp_tired = NumEdit(minimum=-MAX_INT)
        self._bind_int(self.sp_tired, ("Tired",))
        self.sp_balt = NumEdit(maximum=9999)
        self._bind_int(self.sp_balt, ("BaltSlot",))
        grid.addWidget(QLabel("当前HP:"), 0, 0); grid.addWidget(self.sp_hp, 0, 1)
        grid.addWidget(QLabel("当前MP:"), 0, 2); grid.addWidget(self.sp_mp, 0, 3)
        grid.addWidget(QLabel("疲劳 Tired:"), 0, 4); grid.addWidget(self.sp_tired, 0, 5)
        grid.addWidget(QLabel("快捷槽 BaltSlot:"), 1, 0); grid.addWidget(self.sp_balt, 1, 1)

        self.chk_run = QCheckBox("奔跑状态 isRun")
        self._bind_bool(self.chk_run, ("isRun",))
        grid.addWidget(self.chk_run, 1, 2, 1, 2)
        self.chk_sleep = QCheckBox("睡觉中 Sleep")
        self._bind_bool(self.chk_sleep, ("Sleep",))
        grid.addWidget(self.chk_sleep, 1, 4, 1, 2)
        v.addWidget(g)
        v.addStretch(1)
        return page

    def _basic_time_page(self):
        page, v = self._scroll_page()

        # --- 时间 ---
        g = QGroupBox("时间")
        grid = QGridLayout(g)
        self.sp_atime = NumEdit()
        self._bind_int(self.sp_atime, ("activeTime",))
        self.sp_stime = NumEdit()
        self._bind_int(self.sp_stime, ("sleepTime",))
        grid.addWidget(QLabel("activeTime:"), 0, 0); grid.addWidget(self.sp_atime, 0, 1)
        grid.addWidget(QLabel("sleepTime:"), 0, 2); grid.addWidget(self.sp_stime, 0, 3)
        self.sp_gt = []
        for i in range(3):
            s = NumEdit(minimum=-MAX_INT)
            self._bind_int(s, ("GameTime", i))
            grid.addWidget(QLabel("GameTime[%d]:" % i), 1, i * 2)
            grid.addWidget(s, 1, i * 2 + 1)
            self.sp_gt.append(s)
        v.addWidget(g)

        # --- 位置 ---
        g = QGroupBox("位置")
        grid = QGridLayout(g)
        self.cb_scene = QComboBox()
        self.cb_scene.setEditable(True)
        self.cb_scene.addItems(scene_lib())
        self.cb_scene.currentTextChanged.connect(self._on_scene_changed)
        grid.addWidget(QLabel("当前场景 PlayerScene:"), 0, 0)
        grid.addWidget(self.cb_scene, 0, 1, 1, 3)
        self.sp_px = QDoubleSpinBox(); self.sp_px.setRange(-9999, 9999); self.sp_px.setDecimals(4)
        self.sp_py = QDoubleSpinBox(); self.sp_py.setRange(-9999, 9999); self.sp_py.setDecimals(4)
        self.sp_pz = QDoubleSpinBox(); self.sp_pz.setRange(-9999, 9999); self.sp_pz.setDecimals(4)
        self._bind_float(self.sp_px, ("PlayerLocation", "x"))
        self._bind_float(self.sp_py, ("PlayerLocation", "y"))
        self._bind_float(self.sp_pz, ("PlayerLocation", "z"))
        grid.addWidget(QLabel("X:"), 1, 0); grid.addWidget(self.sp_px, 1, 1)
        grid.addWidget(QLabel("Y:"), 1, 2); grid.addWidget(self.sp_py, 1, 3)
        grid.addWidget(QLabel("Z:"), 1, 4); grid.addWidget(self.sp_pz, 1, 5)
        v.addWidget(g)
        v.addStretch(1)
        return page

    def _basic_quick_page(self):
        page, v = self._scroll_page()

        # --- 一键 ---
        g = QGroupBox("一键修改")
        h = QHBoxLayout(g)
        for text, fn in (
            ("金钱 999,999,999", lambda: self._quick(("Money",), 999999999)),
            ("经验 + 熟练度拉满", self._quick_exp),
            ("HP / MP 拉满", self._quick_hp),
            ("全部一键最大", self._quick_all),
            ("清零疲劳", lambda: self._quick(("Tired",), 0)),
        ):
            b = QPushButton(text)
            b.clicked.connect(fn)
            h.addWidget(b)
        h.addStretch(1)
        v.addWidget(g)
        v.addStretch(1)
        return page

    def create_basic_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        self.sub_basic = QTabWidget()
        self.sub_basic.setDocumentMode(True)
        self.sub_basic.addTab(self._basic_role_page(), "角色与状态")
        self.sub_basic.addTab(self._basic_time_page(), "时间与位置")
        self.sub_basic.addTab(self._basic_quick_page(), "一键修改")
        v.addWidget(self.sub_basic, 1)
        return page

    def _on_scene_changed(self, text):
        if self._loading or not self.doc:
            return
        self.doc["PlayerScene"] = text
        self.mark_dirty()

    def _quick(self, path, val):
        if not self._need_doc():
            return
        self._doc_set(path, val)
        self.mark_dirty()
        self._guard(self.refresh_basic)
        self.statusBar().showMessage("已设置 %s = %s"
                                     % (".".join(str(x) for x in path), val), 4000)

    def _quick_exp(self):
        if not self._need_doc():
            return
        self.doc["Experience"] = 999999999
        self.doc["Proficiency"] = 999999999
        self.mark_dirty()
        self._guard(self.refresh_basic)

    def _quick_hp(self):
        if not self._need_doc():
            return
        self.doc["currentHP"] = 999999
        self.doc["currentMP"] = 999999
        self.mark_dirty()
        self._guard(self.refresh_basic)

    def _quick_all(self):
        if not self._need_doc():
            return
        if not ask("把金钱/经验/熟练度/HP/MP 全部拉满，确定？", parent=self):
            return
        self.doc["Money"] = 999999999
        self.doc["Experience"] = 999999999
        self.doc["Proficiency"] = 999999999
        self.doc["currentHP"] = 999999
        self.doc["currentMP"] = 999999
        self.doc["level"] = 99
        self.doc["farmLevel"] = 99
        self.mark_dirty()
        self._guard(self.refresh_basic)

    def refresh_basic(self):
        d = self.doc
        self.ed_name.setText(str(d.get("PlayerName", "")))
        self.sp_money.setValue(int(d.get("Money", 0) or 0))
        self.sp_exp.setValue(int(d.get("Experience", 0) or 0))
        self.sp_prof.setValue(int(d.get("Proficiency", 0) or 0))
        self.sp_level.setValue(int(d.get("level", 0) or 0))
        self.sp_farmlevel.setValue(int(d.get("farmLevel", 0) or 0))
        self.sp_hp.setValue(int(d.get("currentHP", 0) or 0))
        self.sp_mp.setValue(int(d.get("currentMP", 0) or 0))
        self.sp_tired.setValue(int(d.get("Tired", 0) or 0))
        self.sp_balt.setValue(int(d.get("BaltSlot", 0) or 0))
        self.chk_run.setChecked(bool(d.get("isRun", False)))
        self.chk_sleep.setChecked(bool(d.get("Sleep", False)))
        self.sp_atime.setValue(int(d.get("activeTime", 0) or 0))
        self.sp_stime.setValue(int(d.get("sleepTime", 0) or 0))
        gt = d.get("GameTime") or [0, 0, 0]
        for i, s in enumerate(self.sp_gt):
            s.setValue(int(gt[i]) if i < len(gt) else 0)
        self.cb_scene.setCurrentText(str(d.get("PlayerScene", "")))
        loc = d.get("PlayerLocation") or {}
        self.sp_px.setValue(float(loc.get("x", 0) or 0))
        self.sp_py.setValue(float(loc.get("y", 0) or 0))
        self.sp_pz.setValue(float(loc.get("z", 0) or 0))

    # ==================================================================
    # 页签 2：背包 / 工具栏
    # ==================================================================
    BAG_COLS = ["#", "物品名", "ID", "数量", "类型", "攻击", "防御", "暴击", "闪避", "移速", "HP", "UUID"]

    def _make_item_section(self, field, note=""):
        """构造一个物品列表页（供内嵌分页使用）。"""
        page = QWidget()
        v = QVBoxLayout(page)
        if note:
            lb = QLabel(note)
            lb.setStyleSheet("color:#666;")
            lb.setWordWrap(True)
            v.addWidget(lb)

        row = QHBoxLayout()
        for text, fn in (
            ("＋ 添加物品…", lambda: self.on_bag_add(field)),
            ("－ 删除选中", lambda: self.on_bag_delete(field)),
            ("数量改为…", lambda: self.on_bag_set_count(field)),
            ("编辑物品…", lambda: self.on_bag_edit(field)),
        ):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("一键满数量")
        b.clicked.connect(lambda: self.on_bag_max_count(field))
        row.addWidget(b)
        b = QPushButton("清空该列表")
        b.clicked.connect(lambda: self.on_bag_clear(field))
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)

        t = make_table(self.BAG_COLS)
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        t.itemSelectionChanged.connect(lambda: self._bag_table_changed(field))
        v.addWidget(t, 1)
        lbl = QLabel("")
        lbl.setStyleSheet("color:#555;")
        v.addWidget(lbl)

        self.bag_tables[field] = t
        self.bag_labels[field] = lbl
        return page

    def create_bag_tab(self):
        self.bag_tables = {}
        self.bag_labels = {}
        page = QWidget()
        v = QVBoxLayout(page)
        note = QLabel("修改说明：所有操作立即写入内存，点工具栏「保存」后才写回文件。"
                      "同一物品已存在时会自动叠加数量。")
        note.setStyleSheet("color:#666;")
        note.setWordWrap(True)
        v.addWidget(note, 0)
        self.sub_bag = QTabWidget()
        self.sub_bag.setDocumentMode(True)
        self.sub_bag.addTab(self._make_item_section(
            "bagitems", "背包里的全部物品。删除物品时，如正被手持/装备会自动清理引用。"), "背包 bagitems")
        self.sub_bag.addTab(self._make_item_section(
            "toolitems", "工具栏（游戏固定 10 格，超出可能不被游戏识别）。"), "工具栏 toolitems")
        v.addWidget(self.sub_bag, 1)
        return page

    def _selected_rows(self, table):
        return sorted({i.row() for i in table.selectedIndexes()})

    def _bag_table_changed(self, field):
        pass

    def refresh_bag(self):
        for field in ("bagitems", "toolitems"):
            t = self.bag_tables[field]
            lst = self.doc.get(field) or []
            t.setUpdatesEnabled(False)
            t.blockSignals(True)
            t.setRowCount(len(lst))
            for r, e in enumerate(lst):
                it = e.get("item") or {}
                p = e.get("property") or {}
                set_row(t, r, [
                    r + 1, it.get("name", "?"), it.get("id", ""), e.get("count", 0),
                    it.get("itemTypeShow", ""), p.get("attack", 0), p.get("armor", 0),
                    p.get("crit", 0), p.get("dodge", 0), p.get("moveSpeed", 0),
                    p.get("maxHP", 0), e.get("uuid", ""),
                ])
            t.blockSignals(False)
            t.setUpdatesEnabled(True)
            kinds, total = bag_summary(self.doc, field)
            self.bag_labels[field].setText("共 %d 种 / 合计 %s 件" % (kinds, "{:,}".format(total)))

    # ---- 背包操作 ----
    def on_bag_add(self, field):
        if not self._need_doc():
            return
        existing = [e["item"]["id"] for e in (self.doc.get(field) or [])
                    if isinstance(e.get("item"), dict)]
        dlg = ItemPickDialog(self, "选择要添加的物品", item_lib(),
                             existing_ids=existing, count_label="数量")
        if dlg.exec() != QDialog.Accepted:
            return
        added, stacked, failed = bag_add(self.doc, field, dlg.result_ids)
        self.mark_dirty()
        self._guard(self.refresh_bag)
        msg = "新增 %d 种，叠加 %d 种。" % (added, stacked)
        if failed:
            msg += "\n失败：" + "、".join(failed)
        self.statusBar().showMessage(msg, 6000)

    def on_bag_delete(self, field):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.bag_tables[field])
        if not rows:
            warn("请先选中要删除的行（可多选）。", parent=self)
            return
        names = [self.doc[field][r]["item"].get("name", "?") for r in rows]
        if not ask("确定删除以下 %d 项？\n%s" % (len(rows), "、".join(names[:20])), parent=self):
            return
        uuids = bag_delete(self.doc, field, rows)
        fixed = field_fix_after_delete(self.doc, uuids)
        self.mark_dirty()
        self._guard(self.refresh_bag)
        self.statusBar().showMessage(
            "已删除 %d 项%s" % (len(uuids), ("；已清理引用: " + "、".join(fixed)) if fixed else ""),
            6000)

    def on_bag_set_count(self, field):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.bag_tables[field])
        if not rows:
            warn("请先选中要修改的行。", parent=self)
            return
        v, ok = QInputDialog.getInt(self, "修改数量", "把选中的 %d 项数量改为:" % len(rows),
                                    100000000, 0, MAX_COUNT, 1000)
        if not ok:
            return
        for r in rows:
            self.doc[field][r]["count"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_bag)

    def on_bag_max_count(self, field):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.bag_tables[field])
        if not rows:
            warn("请先选中行。", parent=self)
            return
        for r in rows:
            self.doc[field][r]["count"] = MAX_COUNT
        self.mark_dirty()
        self._guard(self.refresh_bag)
        self.statusBar().showMessage("已把 %d 项数量设为 %s"
                                     % (len(rows), "{:,}".format(MAX_COUNT)), 5000)

    def on_bag_clear(self, field):
        if not self._need_doc():
            return
        if not (self.doc.get(field) or []):
            return
        if not ask("确定清空「%s」的全部 %d 条记录？" % (field, len(self.doc[field])), parent=self):
            return
        uuids = [e.get("uuid") for e in (self.doc.get(field) or [])]
        self.doc[field] = []
        fixed = field_fix_after_delete(self.doc, uuids)
        self.mark_dirty()
        self._guard(self.refresh_bag)
        if fixed:
            self.statusBar().showMessage("已清空，并清理引用: " + "、".join(fixed), 6000)

    def on_bag_edit(self, field):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.bag_tables[field])
        if len(rows) != 1:
            warn("请选中 1 行后再编辑。", parent=self)
            return
        e = self.doc[field][rows[0]]
        dlg = ItemEditDialog(self, e, row=rows[0] + 1)
        if dlg.exec() != QDialog.Accepted:
            return
        dlg.apply_to(e)
        self.mark_dirty()
        self._guard(self.refresh_bag)
        self.statusBar().showMessage("已修改 %s" % e["item"].get("name", ""), 4000)

    # ==================================================================
    # 页签 3：武学 / 配方
    # ==================================================================
    def _skill_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("已学武学 / 心法（存档字段 list_skill）。添加时只能从「功法 / 心法」类物品中选。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加武学…", self.on_skill_add),
                         ("－ 删除选中", self.on_skill_del),
                         ("等级改为…", self.on_skill_set_level)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("一键全部满级(4)")
        b.clicked.connect(lambda: self.on_skill_level_all(4))
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_skill = make_table(["#", "武学名", "ID", "等级"])
        self.tb_skill.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_skill, 1)
        self.lbl_skill = QLabel("")
        self.lbl_skill.setStyleSheet("color:#555;")
        v.addWidget(self.lbl_skill)
        return page

    def _skillrun_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("出招栏 list_skillRun：6 个格子，选择「（空）」表示该格不装备（值为 0）。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        self.skillrun_combos = []
        pool = [None] + sorted(gongfa_items(), key=lambda x: x["id"])
        for i in range(6):
            h = QHBoxLayout()
            h.addWidget(QLabel("第 %d 格:" % (i + 1)))
            cb = QComboBox()
            cb.addItem("（空）", 0)
            for it in pool:
                if it:
                    cb.addItem("%s (%s)" % (it["name"], it["id"]), it["id"])
            cb.setEditable(False)
            cb.currentIndexChanged.connect(
                lambda _idx, k=i, w=cb: self._on_skillrun_changed(k, w))
            h.addWidget(cb, 1)
            v.addLayout(h)
            self.skillrun_combos.append(cb)
        v.addStretch(1)
        return page

    def _recipe_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("已学菜谱 / 配方 / 图纸（存档字段 list_recipe）。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加配方…", self.on_recipe_add),
                         ("－ 删除选中", self.on_recipe_del)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("全部学会")
        b.clicked.connect(self.on_recipe_all)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_recipe = make_table(["#", "配方名", "ID"])
        self.tb_recipe.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_recipe, 1)
        self.lbl_recipe = QLabel("")
        self.lbl_recipe.setStyleSheet("color:#555;")
        v.addWidget(self.lbl_recipe)
        return page

    def create_skill_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        self.sub_skill = QTabWidget()
        self.sub_skill.setDocumentMode(True)
        self.sub_skill.addTab(self._skill_page(), "已学武学 list_skill")
        self.sub_skill.addTab(self._skillrun_page(), "出招栏 list_skillRun")
        self.sub_skill.addTab(self._recipe_page(), "配方 list_recipe")
        v.addWidget(self.sub_skill, 1)
        return page

    def refresh_skill(self):
        lst = self.doc.get("list_skill") or []
        self.tb_skill.setRowCount(len(lst))
        for r, e in enumerate(lst):
            set_row(self.tb_skill, r, [r + 1, item_name(e.get("x")), e.get("x"), e.get("y")])
        self.lbl_skill.setText("已学 %d 门（共 %d 门）" % (len(lst), len(gongfa_items())))

        run = self.doc.get("list_skillRun") or []
        for i, cb in enumerate(self.skillrun_combos):
            v = run[i] if i < len(run) else 0
            idx = cb.findData(v)
            cb.setCurrentIndex(idx if idx >= 0 else 0)

        rec = self.doc.get("list_recipe") or []
        self.tb_recipe.setRowCount(len(rec))
        for r, iid in enumerate(rec):
            set_row(self.tb_recipe, r, [r + 1, item_name(iid), iid])
        self.lbl_recipe.setText("已学 %d 项（共 %d 项）" % (len(rec), len(recipe_items())))

    def _on_skillrun_changed(self, idx, combo):
        if self._loading or not self.doc:
            return
        lst = self.doc.setdefault("list_skillRun", [])
        while len(lst) <= idx:
            lst.append(0)
        lst[idx] = int(combo.currentData() or 0)
        self.mark_dirty()

    def on_skill_add(self):
        if not self._need_doc():
            return
        existing = [e.get("x") for e in (self.doc.get("list_skill") or [])]
        dlg = ItemPickDialog(self, "添加武学 / 心法（功法类物品）",
                             pool=gongfa_items(), existing_ids=existing,
                             show_count=False)
        if dlg.exec() != QDialog.Accepted:
            return
        n = list_add_pairs(self.doc, "list_skill", [(i, 4) for i, _ in dlg.result_ids])
        self.mark_dirty()
        self._guard(self.refresh_skill)
        self.statusBar().showMessage("已添加 %d 门武学（等级默认 4）" % n, 5000)

    def on_skill_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_skill)
        if not rows:
            warn("请先选中要删除的行。", parent=self)
            return
        ids = [self.doc["list_skill"][r]["x"] for r in rows]
        if not ask("确定删除 %d 门武学？\n%s"
                   % (len(ids), "、".join(item_name(i) for i in ids[:10])), parent=self):
            return
        n = list_remove_pairs(self.doc, "list_skill", ids)
        # 出招栏里的引用一并清理
        run = self.doc.get("list_skillRun") or []
        self.doc["list_skillRun"] = [0 if x in ids else x for x in run]
        self.mark_dirty()
        self._guard(self.refresh_skill)
        self.statusBar().showMessage("已删除 %d 门" % n, 5000)

    def on_skill_set_level(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_skill)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        v, ok = QInputDialog.getInt(self, "修改等级", "等级改为:", 4, 0, 9999)
        if not ok:
            return
        for r in rows:
            self.doc["list_skill"][r]["y"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_skill)

    def on_skill_level_all(self, v):
        if not self._need_doc():
            return
        for e in self.doc.get("list_skill") or []:
            e["y"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_skill)

    def on_recipe_add(self):
        if not self._need_doc():
            return
        existing = list(self.doc.get("list_recipe") or [])
        dlg = ItemPickDialog(self, "添加菜谱 / 配方 / 图纸",
                             pool=recipe_items(), existing_ids=existing, show_count=False)
        if dlg.exec() != QDialog.Accepted:
            return
        n = list_add_ids(self.doc, "list_recipe", [i for i, _ in dlg.result_ids])
        self.mark_dirty()
        self._guard(self.refresh_skill)
        self.statusBar().showMessage("已添加 %d 项配方" % n, 5000)

    def on_recipe_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_recipe)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        ids = [self.doc["list_recipe"][r] for r in rows]
        n = list_remove_ids(self.doc, "list_recipe", ids)
        self.mark_dirty()
        self._guard(self.refresh_skill)
        self.statusBar().showMessage("已删除 %d 项" % n, 5000)

    def on_recipe_all(self):
        if not self._need_doc():
            return
        n = list_add_ids(self.doc, "list_recipe", [it["id"] for it in recipe_items()])
        self.mark_dirty()
        self._guard(self.refresh_skill)
        info("已学会全部配方，新增 %d 项。" % n, parent=self)
        self.statusBar().showMessage("已学会全部配方（新增 %d 项）" % n, 5000)

    # ==================================================================
    # 页签 4：NPC / 剧情
    # ==================================================================
    def _favor_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("NPC 好感度（存档字段 list_npcFavorItem）。"
                    "favorCount 影响可触发的对话与事件，游戏内上限一般是 100 左右。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加 NPC…", self.on_favor_add),
                         ("－ 删除选中", self.on_favor_del),
                         ("好感改为…", self.on_favor_set)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("全部 999")
        b.clicked.connect(lambda: self.on_favor_all(999))
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_favor = make_table(["#", "NPC", "NPC ID", "好感度", "当前对话ID", "好感事件数"])
        self.tb_favor.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_favor, 1)
        return page

    def _dialogue_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("已触发对话（存档字段 activeDialogues）。"
                    "删除记录会让游戏认为这些对话还没发生过，可能重新播放——慎用。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加对话ID…", self.on_dialogue_add),
                         ("－ 删除选中", self.on_dialogue_del)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("全部清空")
        b.clicked.connect(self.on_dialogue_clear)
        row.addWidget(b)
        row.addStretch(1)
        ed = QLineEdit()
        ed.setPlaceholderText("筛选对话ID…")
        ed.setFixedWidth(180)
        ed.textChanged.connect(self._filter_dialogues)
        row.addWidget(ed)
        self.ed_dlg_filter = ed
        v.addLayout(row)
        self.tb_dialogue = make_table(["#", "对话ID", "overTime"])
        self.tb_dialogue.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_dialogue, 1)
        self.lbl_dialogue = QLabel("")
        self.lbl_dialogue.setStyleSheet("color:#555;")
        v.addWidget(self.lbl_dialogue)
        return page

    def _gifttalk_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("送礼 / 交谈记录（list_giftSend · list_talk），x 为 NPC ID，y 为累计次数。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加…", self.on_gifttalk_add),
                         ("－ 删除选中", self.on_gifttalk_del)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        row.addWidget(QLabel("查看:"))
        self.cb_gifttalk = QComboBox()
        self.cb_gifttalk.addItems(["list_giftSend", "list_talk"])
        self.cb_gifttalk.currentIndexChanged.connect(
            lambda *a: self._guard(self.refresh_gifttalk))
        row.addWidget(self.cb_gifttalk)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_gifttalk = make_table(["#", "NPC", "x", "y"])
        self.tb_gifttalk.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_gifttalk, 1)
        return page

    def _click_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("点击事件计数（存档字段 clickEvents）。"
                    "游戏用这些计数判断「开过几个箱子 / 用过几次工作台」之类的条件，改小可让相关任务重新可做。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        b = QPushButton("次数改为…")
        b.clicked.connect(self.on_click_set)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_click = make_table(["#", "类型 type", "次数"])
        self.tb_click.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_click, 1)
        return page

    def create_npc_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        self.sub_npc = QTabWidget()
        self.sub_npc.setDocumentMode(True)
        self.sub_npc.addTab(self._favor_page(), "NPC 好感")
        self.sub_npc.addTab(self._dialogue_page(), "已触发对话")
        self.sub_npc.addTab(self._gifttalk_page(), "送礼 / 交谈记录")
        self.sub_npc.addTab(self._click_page(), "点击事件")
        v.addWidget(self.sub_npc, 1)
        return page

    def refresh_npc(self):
        lst = self.doc.get("list_npcFavorItem") or []
        self.tb_favor.setRowCount(len(lst))
        for r, e in enumerate(lst):
            set_row(self.tb_favor, r, [
                r + 1, npc_display_name(e.get("npcID")), e.get("npcID"),
                e.get("favorCount", 0), e.get("activeDialogueID", ""),
                len(e.get("favorEvents") or []),
            ])
        self.refresh_dialogues()
        self._guard(self.refresh_gifttalk)
        cl = self.doc.get("clickEvents") or []
        self.tb_click.setRowCount(len(cl))
        for r, e in enumerate(cl):
            set_row(self.tb_click, r, [r + 1, e.get("type", ""), e.get("clickCount", 0)])

    def _filter_dialogues(self, text):
        t = (text or "").strip()
        for r in range(self.tb_dialogue.rowCount()):
            it = self.tb_dialogue.item(r, 1)
            self.tb_dialogue.setRowHidden(r, bool(t) and t not in (it.text() if it else ""))

    def refresh_dialogues(self):
        lst = self.doc.get("activeDialogues") or []
        self.tb_dialogue.setRowCount(len(lst))
        for r, e in enumerate(lst):
            set_row(self.tb_dialogue, r, [r + 1, e.get("dialogueID"), e.get("overTime", 0)])
        self.lbl_dialogue.setText("共 %d 条已触发对话" % len(lst))
        self._filter_dialogues(self.ed_dlg_filter.text() if hasattr(self, "ed_dlg_filter") else "")

    def refresh_gifttalk(self):
        key = self.cb_gifttalk.currentText()
        lst = self.doc.get(key) or []
        self.tb_gifttalk.setRowCount(len(lst))
        for r, e in enumerate(lst):
            set_row(self.tb_gifttalk, r, [r + 1, npc_display_name(e.get("x")), e.get("x"), e.get("y", 0)])

    def on_favor_add(self):
        if not self._need_doc():
            return
        dlg = NpcPickDialog(self, npc_lib(),
                            existing_ids=[e.get("npcID") for e in (self.doc.get("list_npcFavorItem") or [])])
        if dlg.exec() != QDialog.Accepted:
            return
        recs = [{"npcID": nid, "favorCount": 999, "activeDialogueID": -1,
                 "favorEvents": []} for nid in dlg.result_ids]
        n = list_add_dicts(self.doc, "list_npcFavorItem", recs, "npcID")
        self.mark_dirty()
        self._guard(self.refresh_npc)
        self.statusBar().showMessage("已添加 %d 个 NPC 好感记录" % n, 5000)

    def on_favor_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_favor)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        ids = [self.doc["list_npcFavorItem"][r].get("npcID") for r in rows]
        n = list_remove_dicts(self.doc, "list_npcFavorItem", ids, "npcID")
        self.mark_dirty()
        self._guard(self.refresh_npc)
        self.statusBar().showMessage("已删除 %d 条" % n, 5000)

    def on_favor_set(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_favor)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        v, ok = QInputDialog.getInt(self, "修改好感度", "好感度改为:", 999, -99999, 99999)
        if not ok:
            return
        for r in rows:
            self.doc["list_npcFavorItem"][r]["favorCount"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_npc)

    def on_favor_all(self, v):
        if not self._need_doc():
            return
        for e in self.doc.get("list_npcFavorItem") or []:
            e["favorCount"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_npc)

    def on_dialogue_add(self):
        if not self._need_doc():
            return
        txt, ok = QInputDialog.getText(self, "添加对话ID",
                                       "输入对话ID（多个用逗号/空格分隔）:")
        if not ok or not txt.strip():
            return
        ids = [int(x) for x in re.split(r"[\s,，]+", txt.strip()) if x.lstrip("-").isdigit()]
        recs = [{"dialogueID": i, "overTime": 0} for i in ids]
        n = list_add_dicts(self.doc, "activeDialogues", recs, "dialogueID")
        self.mark_dirty()
        self._guard(self.refresh_dialogues)
        self.statusBar().showMessage("已添加 %d 条" % n, 5000)

    def on_dialogue_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_dialogue)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        ids = [self.doc["activeDialogues"][r].get("dialogueID") for r in rows]
        if not ask("删除这 %d 条「已触发对话」记录？\n"
                   "游戏可能会把这些对话当成未触发而重新播放。确定？" % len(ids), parent=self):
            return
        n = list_remove_dicts(self.doc, "activeDialogues", ids, "dialogueID")
        self.mark_dirty()
        self._guard(self.refresh_dialogues)
        self.statusBar().showMessage("已删除 %d 条" % n, 5000)

    def on_dialogue_clear(self):
        if not self._need_doc():
            return
        if not ask("清空全部已触发对话记录？这会让大部分剧情对话重新可触发，风险较高，确定？",
                   parent=self):
            return
        self.doc["activeDialogues"] = []
        self.mark_dirty()
        self._guard(self.refresh_dialogues)

    def on_gifttalk_add(self):
        if not self._need_doc():
            return
        dlg = NpcPickDialog(self, npc_lib(), existing_ids=[])
        if dlg.exec() != QDialog.Accepted:
            return
        key = self.cb_gifttalk.currentText()
        n = list_add_pairs(self.doc, key, [(i, 0) for i in dlg.result_ids])
        self.mark_dirty()
        self._guard(self.refresh_gifttalk)
        self.statusBar().showMessage("已添加 %d 条" % n, 5000)

    def on_gifttalk_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_gifttalk)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        key = self.cb_gifttalk.currentText()
        xs = [self.doc[key][r].get("x") for r in rows]
        n = list_remove_pairs(self.doc, key, xs)
        self.mark_dirty()
        self._guard(self.refresh_gifttalk)
        self.statusBar().showMessage("已删除 %d 条" % n, 5000)

    def on_click_set(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_click)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        v, ok = QInputDialog.getInt(self, "修改点击次数", "次数改为:", 1, 0, MAX_INT)
        if not ok:
            return
        for r in rows:
            self.doc["clickEvents"][r]["clickCount"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_npc)

    # ==================================================================
    # 页签 5：任务
    # ==================================================================
    def create_task_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        g = QGroupBox("任务状态  taskinfos")
        gv = QVBoxLayout(g)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加任务…", self.on_task_add),
                         ("－ 删除选中", self.on_task_del),
                         ("状态改为…", self.on_task_set_state),
                         ("开始/结束时间改为…", self.on_task_set_time)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("全部标记「已完成」")
        b.clicked.connect(lambda: self.on_task_state_all(2))
        row.addWidget(b)
        row.addStretch(1)
        gv.addLayout(row)

        self.tb_task = make_table(["#", "任务ID", "章节", "章节名", "状态", "startTime", "overTime"])
        self.tb_task.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gv.addWidget(self.tb_task, 1)
        self.lbl_task = QLabel("")
        self.lbl_task.setStyleSheet("color:#555;")
        gv.addWidget(self.lbl_task)
        v.addWidget(g, 1)
        return page

    def refresh_task(self):
        lst = self.doc.get("taskinfos") or []
        self.tb_task.setRowCount(len(lst))
        done = 0
        for r, e in enumerate(lst):
            tid = e.get("taskID")
            ch = chapter_map().get(tid) or {}
            st = e.get("state", 0)
            if st == 2:
                done += 1
            set_row(self.tb_task, r, [
                r + 1, tid, ch.get("Chapter", ""), ch.get("Name", ""),
                TASK_STATE_LABELS.get(st, str(st)), e.get("startTime", 0), e.get("overTime", 0)])
        self.lbl_task.setText("共 %d 个任务，已完成 %d 个" % (len(lst), done))

    def on_task_add(self):
        if not self._need_doc():
            return
        have = {e.get("taskID") for e in (self.doc.get("taskinfos") or [])}
        dlg = TaskPickDialog(self, chapter_lib(), existing_ids=have)
        if dlg.exec() != QDialog.Accepted:
            return
        recs = [{"taskID": t, "state": 1, "startTime": 0, "overTime": 0}
                for t in dlg.result_ids]
        n = list_add_dicts(self.doc, "taskinfos", recs, "taskID")
        self.mark_dirty()
        self._guard(self.refresh_task)
        self.statusBar().showMessage("已添加 %d 个任务" % n, 5000)

    def on_task_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_task)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        ids = [self.doc["taskinfos"][r].get("taskID") for r in rows]
        n = list_remove_dicts(self.doc, "taskinfos", ids, "taskID")
        self.mark_dirty()
        self._guard(self.refresh_task)
        self.statusBar().showMessage("已删除 %d 个任务" % n, 5000)

    def on_task_set_state(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_task)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        labels = ["%d - %s" % (k, v) for k, v in sorted(TASK_STATE_LABELS.items())]
        txt, ok = QInputDialog.getItem(self, "任务状态", "状态改为:", labels, 2, False)
        if not ok:
            return
        st = int(txt.split(" - ")[0])
        for r in rows:
            self.doc["taskinfos"][r]["state"] = st
        self.mark_dirty()
        self._guard(self.refresh_task)

    def on_task_state_all(self, st):
        if not self._need_doc():
            return
        for e in self.doc.get("taskinfos") or []:
            e["state"] = int(st)
        self.mark_dirty()
        self._guard(self.refresh_task)

    def on_task_set_time(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_task)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        v, ok = QInputDialog.getInt(self, "时间", "startTime / overTime 改为:", 0, 0, MAX_INT)
        if not ok:
            return
        for r in rows:
            e = self.doc["taskinfos"][r]
            e["startTime"] = int(v)
            e["overTime"] = int(v)
        self.mark_dirty()
        self._guard(self.refresh_task)

    # ==================================================================
    # 页签 6：农场 / 建造
    # ==================================================================
    def _farm_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("农田作物（存档字段 farmitems）。seedTime / waterTime / freeTime 与存档里的 "
                    "activeTime 在同一时间轴上；「全部立即成熟」会把 seedTime 调到已过生长时间。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)

        row = QHBoxLayout()
        for text, fn in (("－ 删除选中地块", self.on_farm_del),
                         ("清空全部农田", self.on_farm_clear)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b1 = QPushButton("全部立即成熟")
        b1.setToolTip("seedTime = waterTime - 生长时间 - 1，让作物被视为已经长好")
        b1.clicked.connect(self.on_farm_mature)
        row.addWidget(b1)
        b2 = QPushButton("全部浇水")
        b2.setToolTip("waterTime = 当前 activeTime")
        b2.clicked.connect(self.on_farm_water_all)
        row.addWidget(b2)
        row.addStretch(1)
        v.addLayout(row)

        g = QGroupBox("批量设置时间（对选中的地块生效）")
        grid = QGridLayout(g)
        self.sp_farm_seed = NumEdit()
        self.sp_farm_water = NumEdit()
        self.sp_farm_free = NumEdit()
        for i, (lab, sp) in enumerate((("seedTime", self.sp_farm_seed),
                                       ("waterTime", self.sp_farm_water),
                                       ("freeTime", self.sp_farm_free))):
            sp.setFixedWidth(140)
            grid.addWidget(QLabel(lab + ":"), 0, i * 2)
            grid.addWidget(sp, 0, i * 2 + 1)
        b = QPushButton("应用于选中")
        b.clicked.connect(self.on_farm_set_time)
        grid.addWidget(b, 0, 6)
        grid.setColumnStretch(7, 1)
        v.addWidget(g)

        self.tb_farm = make_table(["#", "作物", "作物ID", "坐标", "seedTime", "waterTime", "freeTime"])
        self.tb_farm.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_farm, 1)
        self.lbl_farm = QLabel("")
        self.lbl_farm.setStyleSheet("color:#555;")
        v.addWidget(self.lbl_farm)
        return page

    def _build_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("建筑 / 摆放物（存档字段 list_buildinfos）。name 是物品 ID，"
                    "删除后地图上的对应摆放物会消失。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        row = QHBoxLayout()
        b = QPushButton("－ 删除选中建筑")
        b.clicked.connect(self.on_build_del)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.tb_build = make_table(["#", "名称(物品ID)", "物品名", "UUID", "X", "Y", "Z"])
        self.tb_build.setSelectionMode(QAbstractItemView.ExtendedSelection)
        v.addWidget(self.tb_build, 1)
        return page

    def create_farm_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        self.sub_farm = QTabWidget()
        self.sub_farm.setDocumentMode(True)
        self.sub_farm.addTab(self._farm_page(), "农田 farmitems")
        self.sub_farm.addTab(self._build_page(), "建筑 list_buildinfos")
        v.addWidget(self.sub_farm, 1)
        return page

    def refresh_farm(self):
        lst = self.doc.get("farmitems") or []
        self.tb_farm.setRowCount(len(lst))
        counts = {}
        for r, e in enumerate(lst):
            f = e.get("farm") or {}
            pos = e.get("pos") or {}
            counts[f.get("id")] = counts.get(f.get("id"), 0) + 1
            set_row(self.tb_farm, r, [
                r + 1, f.get("name", "?"), f.get("id", ""),
                "(%.1f, %.1f)" % (pos.get("x", 0), pos.get("y", 0)),
                e.get("seedTime", 0), e.get("waterTime", 0), e.get("freeTime", 0)])
        brief = "、".join("%s×%d" % (crop_map().get(k, {}).get("name", k), n)
                          for k, n in sorted(counts.items(), key=lambda x: -x[1])[:8])
        self.lbl_farm.setText("共 %d 块地%s" % (len(lst), ("：" + brief) if brief else ""))

        bl = self.doc.get("list_buildinfos") or []
        self.tb_build.setRowCount(len(bl))
        for r, e in enumerate(bl):
            pos = e.get("pos") or {}
            nm = e.get("name", "")
            show = item_name(int(nm)) if str(nm).isdigit() else nm
            set_row(self.tb_build, r, [r + 1, nm, show, e.get("uuid", ""),
                                       pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)])

    def on_farm_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_farm)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        for r in sorted(rows, reverse=True):
            del self.doc["farmitems"][r]
        self.mark_dirty()
        self._guard(self.refresh_farm)
        self.statusBar().showMessage("已删除 %d 块地" % len(rows), 5000)

    def on_farm_clear(self):
        if not self._need_doc():
            return
        n = len(self.doc.get("farmitems") or [])
        if not n:
            return
        if not ask("清空全部 %d 块农田记录？（地里已种下的东西会消失）" % n, parent=self):
            return
        self.doc["farmitems"] = []
        self.mark_dirty()
        self._guard(self.refresh_farm)

    def on_farm_set_time(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_farm)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        for r in rows:
            e = self.doc["farmitems"][r]
            e["seedTime"] = self.sp_farm_seed.value()
            e["waterTime"] = self.sp_farm_water.value()
            e["freeTime"] = self.sp_farm_free.value()
        self.mark_dirty()
        self._guard(self.refresh_farm)

    def on_farm_mature(self):
        if not self._need_doc():
            return
        lst = self.doc.get("farmitems") or []
        if not lst:
            return
        for e in lst:
            f = e.get("farm") or {}
            grow = int(f.get("growTime", 0) or 0)
            e["seedTime"] = max(0, int(e.get("waterTime", 0) or 0) - max(grow, 1) - 1)
        self.mark_dirty()
        self._guard(self.refresh_farm)
        info("已把 %d 块地的 seedTime 调到「已过生长时间」，进游戏后作物应当可以收获。\n"
             "（若游戏另有浇水/生长判定，请等待一个游戏日或手动浇一次水）" % len(lst), parent=self)

    def on_farm_water_all(self):
        if not self._need_doc():
            return
        now = int(self.doc.get("activeTime", 0) or 0)
        for e in self.doc.get("farmitems") or []:
            e["waterTime"] = now
        self.mark_dirty()
        self._guard(self.refresh_farm)

    def on_build_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_build)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        for r in sorted(rows, reverse=True):
            del self.doc["list_buildinfos"][r]
        self.mark_dirty()
        self._guard(self.refresh_farm)

    # ==================================================================
    # 页签 7：世界 / 杂项
    # ==================================================================
    def create_world_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)

        g = QGroupBox("已激活场景  activeScene（可访问的地图清单）")
        gv = QVBoxLayout(g)
        row = QHBoxLayout()
        for text, fn in (("＋ 添加场景…", self.on_scene_add),
                         ("－ 删除选中", self.on_scene_del)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("解锁全部场景")
        b.clicked.connect(self.on_scene_all)
        row.addWidget(b)
        row.addStretch(1)
        gv.addLayout(row)
        self.tb_scene = make_table(["#", "场景标识", "说明"])
        self.tb_scene.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gv.addWidget(self.tb_scene, 1)
        self.lbl_scene = QLabel("")
        self.lbl_scene.setStyleSheet("color:#555;")
        gv.addWidget(self.lbl_scene)
        v.addWidget(g, 1)

        g = QGroupBox("ListScene / 制作队列 / 装备引用 等")
        gv = QVBoxLayout(g)
        row = QHBoxLayout()
        b = QPushButton("制作队列 makeCraftInfos 清空")
        b.clicked.connect(self.on_craft_clear)
        row.addWidget(b)
        b = QPushButton("装备引用 list_equipment 清空")
        b.clicked.connect(self.on_equipment_clear)
        row.addWidget(b)
        b = QPushButton("已破坏物件 scenesDestroyID 清空")
        b.clicked.connect(self.on_destroy_clear)
        row.addWidget(b)
        b = QPushButton("已点击对象 list_clickedObj 清空")
        b.clicked.connect(self.on_clickedobj_clear)
        row.addWidget(b)
        row.addStretch(1)
        gv.addLayout(row)
        self.lbl_misc = QLabel("")
        self.lbl_misc.setWordWrap(True)
        self.lbl_misc.setStyleSheet("color:#444;")
        gv.addWidget(self.lbl_misc)
        v.addWidget(g)

        g = QGroupBox("手动改数值（原样 JSON）")
        grid = QGridLayout(g)
        self.world_spins = {}
        items = [("装备槽 Equipment", "Equipment", True),
                 ("天赋栏 Perk", "Perk", True),
                 ("快捷槽 BaltSlot", "BaltSlot", False),
                 ("疲劳 Tired", "Tired", False)]
        r = 0
        for label, key, is_list in items:
            grid.addWidget(QLabel(label + ":"), r, 0)
            if is_list:
                cur = self.doc.get(key) if self.doc else []
                n = len(cur) if isinstance(cur, list) else 0
                n = max(n, 6 if key == "Perk" else 4)
                sps = []
                for i in range(n):
                    sp = NumEdit(minimum=-MAX_INT)
                    sp.setMaximumWidth(150)
                    sp.valueChanged.connect(
                        lambda val, k=key, ix=i: self._on_world_list(k, ix, val))
                    grid.addWidget(sp, r, i + 1)
                    sps.append(sp)
                self.world_spins[key] = sps
            else:
                sp = NumEdit(minimum=-MAX_INT)
                sp.setMaximumWidth(150)
                sp.valueChanged.connect(lambda val, k=key: self._on_world_scalar(k, val))
                grid.addWidget(sp, r, 1)
                self.world_spins[key] = sp
            r += 1
        v.addWidget(g)
        v.addStretch(1)
        return page

    def _on_world_list(self, key, idx, val):
        if self._loading or not self.doc:
            return
        lst = self.doc.setdefault(key, [])
        while len(lst) <= idx:
            lst.append(0)
        lst[idx] = int(val)
        self.mark_dirty()

    def _on_world_scalar(self, key, val):
        if self._loading or not self.doc:
            return
        self.doc[key] = int(val)
        self.mark_dirty()

    def refresh_world(self):
        lst = self.doc.get("activeScene") or []
        self.tb_scene.setRowCount(len(lst))
        for r, s in enumerate(lst):
            set_row(self.tb_scene, r, [r + 1, s, ""])
        self.lbl_scene.setText("已激活 %d 个场景（场景库共 %d 个）" % (len(lst), len(scene_lib())))
        self.lbl_misc.setText(
            "ListScene: %s\n制作队列 makeCraftInfos: %d 条\n装备引用 list_equipment: %d 条\n"
            "已破坏物件 scenesDestroyID: %d 条\n已点击对象 list_clickedObj: %d 条\n"
            "标记 Marker: %d 条 · 记忆 ListMemory: %d 条 · 悬赏 Bounty: %d 条"
            % (", ".join(self.doc.get("ListScene") or []) or "（空）",
               len(self.doc.get("makeCraftInfos") or []),
               len(self.doc.get("list_equipment") or []),
               len(self.doc.get("scenesDestroyID") or []),
               len(self.doc.get("list_clickedObj") or []),
               len(self.doc.get("Marker") or []),
               len(self.doc.get("ListMemory") or []),
               len(self.doc.get("Bounty") or [])))
        for key, w in self.world_spins.items():
            if isinstance(w, list):
                cur = self.doc.get(key) or []
                for i, sp in enumerate(w):
                    sp.setValue(int(cur[i]) if i < len(cur) else 0)
            else:
                w.setValue(int(self.doc.get(key, 0) or 0))

    def on_scene_add(self):
        if not self._need_doc():
            return
        have = set(self.doc.get("activeScene") or [])
        pool = [{"id": s, "name": s, "nameKey": s, "itemTypeShow": "场景"}
                for s in scene_lib() if s not in have]
        dlg = SimplePickDialog(self, "添加场景", pool, show_count=False,
                               headers=["场景标识"])
        if dlg.exec() != QDialog.Accepted:
            return
        n = list_add_ids(self.doc, "activeScene", dlg.result_ids)
        self.mark_dirty()
        self._guard(self.refresh_world)
        self.statusBar().showMessage("已添加 %d 个场景" % n, 5000)

    def on_scene_del(self):
        if not self._need_doc():
            return
        rows = self._selected_rows(self.tb_scene)
        if not rows:
            warn("请先选中行。", parent=self)
            return
        ids = [self.doc["activeScene"][r] for r in rows]
        if not ask("删除 %d 个已激活场景？\n（当前所在场景请不要删）" % len(ids), parent=self):
            return
        n = list_remove_ids(self.doc, "activeScene", ids)
        self.mark_dirty()
        self._guard(self.refresh_world)
        self.statusBar().showMessage("已删除 %d 个" % n, 5000)

    def on_scene_all(self):
        if not self._need_doc():
            return
        n = list_add_ids(self.doc, "activeScene", scene_lib())
        self.mark_dirty()
        self._guard(self.refresh_world)
        info("已解锁全部场景，新增 %d 个。" % n, parent=self)

    def on_craft_clear(self):
        if not self._need_doc():
            return
        n = len(self.doc.get("makeCraftInfos") or [])
        if n and ask("清空 %d 条制作队列记录？" % n, parent=self):
            self.doc["makeCraftInfos"] = []
            self.mark_dirty()
            self._guard(self.refresh_world)

    def on_equipment_clear(self):
        if not self._need_doc():
            return
        n = len(self.doc.get("list_equipment") or [])
        if n and ask("清空 %d 条装备引用？（已装备的饰品会卸下）" % n, parent=self):
            self.doc["list_equipment"] = []
            self.mark_dirty()
            self._guard(self.refresh_world)

    def on_destroy_clear(self):
        if not self._need_doc():
            return
        n = len(self.doc.get("scenesDestroyID") or [])
        if n and ask("清空 %d 条「已破坏/已采集物件」记录？\n"
                     "清空后地图上的草药、树木等资源可能重新出现（也可能造成异常），确定？" % n,
                     parent=self):
            self.doc["scenesDestroyID"] = []
            self.mark_dirty()
            self._guard(self.refresh_world)

    def on_clickedobj_clear(self):
        if not self._need_doc():
            return
        n = len(self.doc.get("list_clickedObj") or [])
        if n and ask("清空 %d 条「已点击对象」记录？" % n, parent=self):
            self.doc["list_clickedObj"] = []
            self.mark_dirty()
            self._guard(self.refresh_world)

    # ==================================================================
    # 页签 8：高级
    # ==================================================================
    def _json_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("直接编辑整份存档 JSON（危险操作，请先备份）。"
                    "修改后点「应用文本」，程序会做 JSON 合法性校验，通过后才写入内存"
                    "（仍需点工具栏「保存」才写回文件）。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        self.txt_json = QPlainTextEdit()
        self.txt_json.setFont(QFont("Consolas", 9))
        self.txt_json.setLineWrapMode(QPlainTextEdit.NoWrap)
        v.addWidget(self.txt_json, 1)
        row = QHBoxLayout()
        b = QPushButton("从当前数据刷新文本")
        b.clicked.connect(lambda: self._guard(self.refresh_adv))
        row.addWidget(b)
        b = QPushButton("应用文本（校验后写入内存）")
        b.clicked.connect(self.on_apply_json_text)
        row.addWidget(b)
        b = QPushButton("格式化（缩进显示）")
        b.clicked.connect(self.on_format_json_text)
        row.addWidget(b)
        b = QPushButton("校验存档完整性")
        b.clicked.connect(self.on_validate)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        return page

    def _backup_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        lb = QLabel("每次保存前会自动把原存档复制到程序目录的 backups\\ 下，"
                    "最多保留「设置」里配置的份数。")
        lb.setStyleSheet("color:#666;")
        lb.setWordWrap(True)
        v.addWidget(lb)
        self.lst_backup = QListWidget()
        v.addWidget(self.lst_backup, 1)
        row = QHBoxLayout()
        b = QPushButton("刷新列表")
        b.clicked.connect(self.refresh_backups)
        row.addWidget(b)
        b = QPushButton("把选中备份还原到存档槽…")
        b.clicked.connect(self.on_restore_backup)
        row.addWidget(b)
        b = QPushButton("删除选中备份")
        b.clicked.connect(self.on_delete_backup)
        row.addWidget(b)
        b = QPushButton("打开备份目录")
        b.clicked.connect(self.on_open_backup_dir)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        return page

    def create_adv_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        self.sub_adv = QTabWidget()
        self.sub_adv.setDocumentMode(True)
        self.sub_adv.addTab(self._json_page(), "JSON 文本编辑")
        self.sub_adv.addTab(self._backup_page(), "备份管理")
        v.addWidget(self.sub_adv, 1)
        return page

    def refresh_adv(self):
        if self.doc:
            self.txt_json.setPlainText(dumps_save(self.doc))
        self.refresh_backups()

    def on_format_json_text(self):
        try:
            d = json.loads(self.txt_json.toPlainText())
        except Exception as e:
            warn("JSON 解析失败：\n%s" % e, parent=self)
            return
        self.txt_json.setPlainText(json.dumps(d, ensure_ascii=False, indent=1))

    def on_apply_json_text(self):
        txt = self.txt_json.toPlainText()
        try:
            d = json.loads(txt, parse_float=RawFloat)
        except Exception as e:
            warn("JSON 解析失败，未应用：\n%s" % e, parent=self)
            return
        if not isinstance(d, dict):
            warn("根节点必须是对象。", parent=self)
            return
        if not ask("用文本内容替换当前内存中的存档数据？\n（不会立即写盘，仍需点「保存」）", parent=self):
            return
        self.doc = d
        self.mark_dirty()
        self._guard(self.refresh_all)
        self.statusBar().showMessage("已应用文本内容", 5000)

    def on_validate(self):
        if not self._need_doc():
            return
        msgs = []
        try:
            text = dumps_save(self.doc)
            json.loads(text)
            msgs.append("✅ JSON 合法，序列化长度 %s 字节" % "{:,}".format(len(text)))
        except Exception as e:
            msgs.append("❌ JSON 非法: %s" % e)
        # 关键字段检查
        need = ["PlayerName", "Money", "bagitems", "toolitems", "activeScene",
                "list_skill", "list_skillRun", "taskinfos", "activeDialogues"]
        miss = [k for k in need if k not in self.doc]
        msgs.append(("✅ 关键字段齐全" if not miss else "⚠️ 缺少字段: " + "、".join(miss)))
        # 类型检查
        bad = []
        for k in ("Money", "Experience", "level", "currentHP"):
            if k in self.doc and not isinstance(self.doc[k], int):
                bad.append(k)
        msgs.append(("✅ 数值字段类型正确" if not bad else "⚠️ 类型异常: " + "、".join(bad)))
        # 物品 id 检查
        unknown = set()
        for f in ("bagitems", "toolitems"):
            for e in self.doc.get(f) or []:
                iid = (e.get("item") or {}).get("id")
                if iid not in item_map():
                    unknown.add(iid)
        msgs.append("✅ 全部物品 ID 都在物品库中" if not unknown
                    else "⚠️ 未知物品 ID: %s" % sorted(unknown)[:20])
        # 装备引用
        uuids = {(e.get("uuid")) for f in ("bagitems", "toolitems") for e in self.doc.get(f) or []}
        dangling = [u for u in (self.doc.get("list_equipment") or []) if u not in uuids]
        msgs.append("✅ 装备引用有效" if not dangling else "⚠️ 失效装备引用: %d 条" % len(dangling))
        info("\n".join(msgs), title="存档校验", parent=self)

    # ---- 备份 ----
    def refresh_backups(self):
        d = backup_dir()
        self.lst_backup.clear()
        try:
            files = sorted((f for f in os.listdir(d) if f.lower().endswith(".json")),
                           reverse=True)
        except Exception:
            files = []
        for f in files:
            p = os.path.join(d, f)
            try:
                sz = os.path.getsize(p) / 1024.0
                tm = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                sz, tm = 0, ""
            it = QListWidgetItem("%s   （%.1f KB, %s）" % (f, sz, tm))
            it.setData(Qt.UserRole, p)
            self.lst_backup.addItem(it)

    def on_restore_backup(self):
        it = self.lst_backup.currentItem()
        if not it:
            warn("请先选中一个备份。", parent=self)
            return
        src = it.data(Qt.UserRole)
        if not ask("把备份\n%s\n还原到哪个槽？\n\n（会覆盖对应存档，原文件会先自动备份）" % os.path.basename(src),
                   parent=self):
            return
        labels = ["槽%d (save%dplayer.json)" % (i + 1, i) for i in range(SLOT_COUNT)]
        txt, ok = QInputDialog.getItem(self, "选择存档槽", "还原到:", labels, self.slot, False)
        if not ok:
            return
        slot = labels.index(txt)
        dst = slot_player_path(self.save_dir, slot)
        if os.path.isfile(dst):
            backup_save(dst)
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        except Exception as e:
            warn("还原失败：\n%s" % e, parent=self)
            return
        self.refresh_slots()
        if self.path == dst:
            self.load_file(dst)
        info("已还原到 %s" % dst, parent=self)

    def on_delete_backup(self):
        it = self.lst_backup.currentItem()
        if not it:
            return
        p = it.data(Qt.UserRole)
        if ask("删除备份 %s ？" % os.path.basename(p), parent=self):
            try:
                os.remove(p)
            except Exception as e:
                warn("删除失败：%s" % e, parent=self)
            self.refresh_backups()

    def on_open_backup_dir(self):
        d = backup_dir()
        try:
            os.startfile(d)
        except Exception:
            info("备份目录：\n%s" % d, parent=self)

    # ==================================================================
    # 全量刷新
    # ==================================================================
    def refresh_all(self):
        self.refresh_basic()
        self.refresh_bag()
        self.refresh_skill()
        self.refresh_npc()
        self.refresh_task()
        self.refresh_farm()
        self.refresh_world()
        self.refresh_adv()







# ======================================================================
# 九、其它对话框
# ======================================================================

class ItemEditDialog(QDialog):
    """编辑单条物品记录：数量、物品等级、装备属性。"""

    PROP_FIELDS = ["minAttack", "maxAttack", "attack", "minArmor", "maxArmor", "armor",
                   "crit", "critHit", "moveSpeed", "dodge", "maxHP"]

    def __init__(self, parent, entry, row=0):
        super().__init__(parent)
        self.setWindowTitle("编辑物品（第 %d 行）" % row)
        self.resize(560, 520)
        self._entry = entry
        self._build()

    def _build(self):
        e = self._entry
        it = e.get("item") or {}
        v = QVBoxLayout(self)

        head = QLabel("<b>%s</b> &nbsp; ID=%s &nbsp; 类型=%s / %s"
                      % (it.get("name", "?"), it.get("id", ""),
                         it.get("type", ""), it.get("itemTypeShow", "")))
        v.addWidget(head)

        f = QFormLayout()
        self.sp_count = NumEdit()
        self.sp_count.setValue(int(e.get("count", 0)))
        f.addRow("数量 count:", self.sp_count)
        self.sp_ilevel = NumEdit(maximum=9999)
        self.sp_ilevel.setValue(int(it.get("level", 0) or 0))
        f.addRow("物品 level:", self.sp_ilevel)
        self.ed_uuid = QLineEdit(str(e.get("uuid", "")))
        f.addRow("uuid:", self.ed_uuid)
        v.addLayout(f)

        g = QGroupBox("装备属性 property（非装备类物品一般全为 0）")
        grid = QGridLayout(g)
        self.prop_spins = {}
        p = e.get("property") or {}
        for i, k in enumerate(self.PROP_FIELDS):
            sp = NumEdit(minimum=-MAX_INT)
            sp.setValue(int(p.get(k, 0) or 0))
            r, c = divmod(i, 3)
            grid.addWidget(QLabel(k + ":"), r, c * 2)
            grid.addWidget(sp, r, c * 2 + 1)
            self.prop_spins[k] = sp
        btn = QPushButton("全部归零")
        btn.clicked.connect(lambda: [s.setValue(0) for s in self.prop_spins.values()])
        grid.addWidget(btn, (len(self.PROP_FIELDS) + 2) // 3, 0, 1, 2)
        v.addWidget(g)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("确定")
        bb.button(QDialogButtonBox.Cancel).setText("取消")
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def apply_to(self, entry):
        entry["count"] = self.sp_count.value()
        entry.setdefault("item", {})["level"] = self.sp_ilevel.value()
        u = self.ed_uuid.text().strip()
        if u:
            entry["uuid"] = u
        prop = entry.setdefault("property", {})
        for k, sp in self.prop_spins.items():
            prop[k] = sp.value()


class SimplePickDialog(QDialog):
    """通用「带搜索的多选列表」对话框；pool 为 [{id,name,...}]。"""

    def __init__(self, parent=None, title="选择", pool=None, existing_ids=None,
                 show_count=False, default_count=1, headers=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 560)
        self._pool = list(pool or [])
        self._existing = set(existing_ids or ())
        self.headers = headers or ["名称", "ID"]
        self.result_ids = []
        self._show_count = show_count
        self._build(default_count)

    def _build(self, default_count):
        v = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("搜索:"))
        self.ed = QLineEdit()
        self.ed.textChanged.connect(self._filter)
        row.addWidget(self.ed, 1)
        v.addLayout(row)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(self.headers)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.itemDoubleClicked.connect(lambda *a: self.accept())
        v.addWidget(self.tree, 1)

        for r in self._pool:
            cols = [str(r.get("name", "")), str(r.get("id", ""))]
            if len(self.headers) > len(cols):
                cols += [""] * (len(self.headers) - len(cols))
            it = QTreeWidgetItem(cols[:len(self.headers)])
            it.setData(0, Qt.UserRole, r.get("id"))
            if r.get("id") in self._existing:
                it.setForeground(0, QBrush(QColor("#888888")))
                it.setToolTip(0, "已存在")
            self.tree.addTopLevelItem(it)

        self.lbl = QLabel("")
        v.addWidget(self.lbl)
        bot = QHBoxLayout()
        if self._show_count:
            bot.addWidget(QLabel("数量:"))
            self.sp_count = NumEdit(minimum=1, maximum=MAX_COUNT)
            self.sp_count.setValue(default_count)
            bot.addWidget(self.sp_count)
        else:
            self.sp_count = None
        b = QPushButton("全选当前列表")
        b.clicked.connect(self._select_all)
        bot.addWidget(b)
        bot.addStretch(1)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("确定")
        bb.button(QDialogButtonBox.Cancel).setText("取消")
        bb.accepted.connect(self._on_ok)
        bb.rejected.connect(self.reject)
        bot.addWidget(bb)
        v.addLayout(bot)
        self._filter("")

    def _filter(self, text):
        t = (text or "").strip().lower()
        shown = 0
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            blob = " ".join(it.text(c) for c in range(self.tree.columnCount())).lower()
            ok = (not t) or all(k in blob for k in re.split(r"[\s,，]+", t) if k)
            it.setHidden(not ok)
            if ok:
                shown += 1
        self.lbl.setText("共 %d 项，显示 %d 项，已选 %d 项"
                         % (len(self._pool), shown, len(self.tree.selectedItems())))

    def _select_all(self):
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            if not it.isHidden():
                it.setSelected(True)
        self._filter(self.ed.text())

    def _on_ok(self):
        ids = [x.data(0, Qt.UserRole) for x in self.tree.selectedItems()]
        if not ids:
            warn("请先选择。", parent=self)
            return
        cnt = self.sp_count.value() if self.sp_count else 1
        self.result_ids = [(i, cnt) for i in ids]
        self.accept()


class NpcPickDialog(SimplePickDialog):
    def __init__(self, parent=None, pool=None, existing_ids=None):
        rows = [{"id": n["id"],
                 "name": (n.get("name") or "") + ("(%s)" % n["key"] if n.get("key") else ""),
                 "key": n.get("key", "")} for n in (pool or [])]
        rows.sort(key=lambda r: (r["id"] or 0))
        super().__init__(parent, "选择 NPC", rows, existing_ids=existing_ids,
                         show_count=False, headers=["NPC", "ID"])


class TaskPickDialog(SimplePickDialog):
    def __init__(self, parent=None, pool=None, existing_ids=None):
        rows = [{"id": c["id"], "name": "%s / %s" % (c.get("Chapter", ""), c.get("Name", "")),
                 "Chapter": c.get("Chapter", ""), "Description": c.get("Description", "")}
                for c in (pool or [])]
        rows.sort(key=lambda r: r["id"])
        super().__init__(parent, "选择任务（章节）", rows, existing_ids=existing_ids,
                         show_count=False,
                         headers=["章节 / 名称", "任务ID"])


# ======================================================================
# 十、入口
# ======================================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    if not item_lib():
        QMessageBox.warning(
            None, "数据表缺失",
            "未找到 data\\ 目录下的数据表文件。\n\n"
            "请确认 data 目录与程序在同一目录下（编译后需一起分发）。\n"
            "程序仍可运行，但物品列表会是空的。")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



