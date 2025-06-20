# algorithm from https://greasyfork.org/zh-CN/scripts/434334
# transcribed by Deepseek R1
import asyncio

def make_crc32_table() -> list[int]:
    """生成CRC32查表"""
    poly = 0xedb88320
    table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = ((crc >> 1) ^ poly) & 0xFFFFFFFF
            else:
                crc = (crc >> 1) & 0xFFFFFFFF
        table[i] = crc
    return table

def update_crc(byte: int, crc: int, table: list[int]) -> int:
    """更新CRC32值"""
    index = (crc & 0xFF) ^ byte
    value = table[index]
    return ((crc >> 8) ^ value) & 0xFFFFFFFF

def compute(arr: list[int], init_crc: int|None, table: list[int]) -> int:
    """计算字节数组的CRC32值"""
    crc = init_crc if init_crc is not None else 0
    for byte in arr:
        crc = update_crc(byte, crc, table)
    return crc

class Crc32Cracker:
    """CRC32反向查询器"""
    
    def __init__(self) -> None:
        # 初始化查表和预计算数据
        self.table: list[int] = make_crc32_table()
        self.rainbow_0: list[int] = self._make_rainbow(100000)
        self.rainbow_1: list[int] = self._make_rainbow_1()
        self.rainbow_pos: list[int]
        self.rainbow_hash: list[int]
        self.rainbow_pos, self.rainbow_hash = self._make_hash()

    def _make_rainbow(self, n: int) -> list[int]:
        """生成基础彩虹表"""
        return [self._compute_number_crc(i) for i in range(n)]

    def _compute_number_crc(self, number: int) -> int:
        """计算数字字符串形式的CRC值"""
        digits = list(map(int, str(number)))
        return compute(digits, 0, self.table)

    def _make_rainbow_1(self) -> list[int]:
        """生成带5个零后缀的彩虹表"""
        five_zeros = [0] * 5
        return [compute(five_zeros, crc, self.table) for crc in self.rainbow_0]

    def _make_hash(self) -> tuple[list[int], list[int]]:
        """构建哈希加速结构"""
        # 初始化位置索引表
        pos_table = [0] * 65537  # 存储65536个分区的索引
        
        # 统计每个高16位的出现次数
        for crc in self.rainbow_0:
            high16 = crc >> 16
            pos_table[high16] += 1
        
        # 计算前缀和
        for i in range(1, 65536 + 1):
            pos_table[i] += pos_table[i - 1]
        
        # 初始化哈希存储表
        hash_table = [0] * (200_000 * 2)  # 每个元素占两个位置
        
        # 反向填充哈希表
        for i in reversed(range(len(self.rainbow_0))):
            crc = self.rainbow_0[i]
            high16 = crc >> 16
            pos_table[high16] -= 1
            pos = pos_table[high16]
            hash_table[pos * 2] = crc
            hash_table[pos * 2 + 1] = i
        
        return pos_table, hash_table

    def _lookup(self, target_crc: int) -> list[int]:
        """在哈希表中查找候选UID"""
        high16 = target_crc >> 16
        if high16 > 65535:
            return []
        
        first = self.rainbow_pos[high16]
        last = self.rainbow_pos[high16 + 1]
        results = []
        
        for i in range(first, last):
            idx = i * 2
            if self.rainbow_hash[idx] == target_crc:
                results.append(self.rainbow_hash[idx + 1])
        
        return results

    def crack(self, main_crc: int, max_digits: int = 10) -> list[int]:
        """主破解函数"""
        results: list[int] = []
        inverted_crc = (~main_crc) & 0xFFFFFFFF
        base_crc = 0xFFFFFFFF
        
        for num_digits in range(1, max_digits + 1):
            # 更新基准CRC（模拟添加位数前缀）
            base_crc = update_crc(0x30, base_crc, self.table)
            
            if num_digits < 6:
                # 直接暴力搜索短UID
                start = 10 ** (num_digits - 1)
                end = 10 ** num_digits
                for uid in range(start, end):
                    if uid >= len(self.rainbow_0):
                        continue
                    if (base_crc ^ self.rainbow_0[uid]) & 0xFFFFFFFF == inverted_crc:
                        results.append(uid)
            else:
                # 使用彩虹表加速长UID搜索
                prefix_start = 10 ** (num_digits - 6)
                prefix_end = 10 ** (num_digits - 5)
                for prefix in range(prefix_start, prefix_end):
                    if prefix >= len(self.rainbow_1):
                        continue
                    remainder = (inverted_crc ^ base_crc ^ self.rainbow_1[prefix]) & 0xFFFFFFFF
                    candidates = self._lookup(remainder)
                    for suffix in candidates:
                        results.append(prefix * 100_000 + suffix)
        
        return results

# 单例实例
_cracker_instance: Crc32Cracker|None = None

def uhash2uid(uid_hash: str, max_digits: int = 10) -> list[int]:
    """对外接口：将CRC哈希转换为可能的UID"""
    global _cracker_instance
    if _cracker_instance is None:
        _cracker_instance = Crc32Cracker()
    target_crc = int(uid_hash, 16)
    return _cracker_instance.crack(target_crc, max_digits)

async def uhash2uid_async(uid_hash: str, max_digits: int = 10) -> list[int]:
    """对外接口：将CRC哈希转换为可能的UID"""
    await asyncio.to_thread(uhash2uid, uid_hash=uid_hash, max_digits=max_digits)