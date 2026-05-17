from __future__ import annotations

from terminal.context import Context, Unit
from .base import BaseRotation


class HunterBeastMastery(BaseRotation):
    name = "野兽控制"
    desc = "野兽控制猎人循环。"

    def __init__(self) -> None:
        super().__init__()

        self.macroTable = {
            "误导": "ALT-NUMPAD1",
            "召唤宠物": "ALT-NUMPAD2",
            "复活宠物": "ALT-NUMPAD3",
            "target杀戮命令": "ALT-NUMPAD4",
            "target狂野怒火": "ALT-NUMPAD5",
            "target狂野鞭笞": "ALT-NUMPAD6",
            "target猎人印记": "ALT-NUMPAD7",
            "target宁神射击": "ALT-NUMPAD8",
            "target反制射击": "ALT-NUMPAD9",
            "focus反制射击": "ALT-NUMPAD0",
            "target眼镜蛇射击": "SHIFT-NUMPAD1",
            "focus宁神射击": "SHIFT-NUMPAD2",
        }

    def _needs_interrupt(
        self,
        unit: Unit,
        interrupt_blacklist: list[str],
    ) -> bool:
        if not unit.exists or not unit.canAttack or not unit.isInRangedRange:
            return False
        if unit.anyCastIcon is None or not unit.anyCastIsInterruptible:
            return False
        return unit.anyCastIcon not in interrupt_blacklist

    def _needs_enemy_dispel(self, unit: Unit, dispel_blacklist: list[str]) -> bool:
        if not unit.exists or not unit.canAttack or not unit.isInRangedRange:
            return False
        for aura in unit.debuff:
            if aura.type == "DEBUFF_ON_ENEMY" and aura.title not in dispel_blacklist:
                return True
        return False

    def main_rotation(self, ctx: Context) -> tuple[str, float, str]:
        if not ctx.enable:
            return self.idle("总开关未开启")

        if ctx.delay:
            return self.idle("延迟开关开启")

        spell_queue_window = float(ctx.spell_queue_window or 0.3)
        player = ctx.player
        target = ctx.target
        focus = ctx.focus

        if not player.alive:
            return self.idle("玩家已死亡")

        if player.isChatInputActive:
            return self.idle("正在聊天输入")

        if player.isMounted:
            return self.idle("骑乘中")

        if player.castIcon is not None:
            return self.idle("正在施法")

        if player.channelIcon is not None:
            return self.idle("正在引导")

        if player.isEmpowering:
            return self.idle("正在蓄力")

        if player.hasBuff("食物和饮料"):
            return self.idle("正在吃喝")

        if not player.isInCombat:
            return self.idle("未进入战斗")

        focus_need_interrupt = self._needs_interrupt(focus, ctx.interrupt_blacklist)
        target_need_interrupt = self._needs_interrupt(target, ctx.interrupt_blacklist)
        if ctx.spell_cooldown_ready("反制射击", spell_queue_window, ignore_gcd=True):
            if focus_need_interrupt:
                return self.cast("focus反制射击")
            if target_need_interrupt:
                return self.cast("target反制射击")

        focus_need_dispel = self._needs_enemy_dispel(focus, ctx.dispel_blacklist)
        target_need_dispel = self._needs_enemy_dispel(target, ctx.dispel_blacklist)
        if ctx.spell_cooldown_ready("宁神射击", spell_queue_window, ignore_gcd=True):
            if focus_need_dispel:
                return self.cast("focus宁神射击")
            if target_need_dispel:
                return self.cast("target宁神射击")

        if target.exists and target.canAttack and target.isInCombat:
            if ctx.assisted_combat == "杀戮命令":
                return self.cast("target杀戮命令")
            if ctx.assisted_combat == "狂野怒火":
                return self.cast("target狂野怒火")
            if ctx.assisted_combat == "狂野鞭笞":
                return self.cast("target狂野鞭笞")
            if ctx.assisted_combat == "猎人印记":
                return self.cast("target猎人印记")
            if ctx.assisted_combat == "宁神射击":
                return self.cast("target宁神射击")
            if ctx.assisted_combat == "眼镜蛇射击":
                return self.cast("target眼镜蛇射击")

        return self.idle("当前没有合适动作")
