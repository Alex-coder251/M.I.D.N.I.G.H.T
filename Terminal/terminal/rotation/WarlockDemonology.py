from __future__ import annotations

from terminal.context import Context
from .base import BaseRotation


class WarlockDemonology(BaseRotation):
    name = "恶魔术灵魂收割者"
    desc = "恶魔学识术士灵魂收割者大秘境循环。"

    def __init__(self) -> None:
        super().__init__()

        self.macroTable = {
            "target鍙ゅ皵涓逛箣鎵?": "ALT-NUMPAD1",
            "鍙敜鍦扮嫳鐚庣姮": "ALT-NUMPAD2",
            "鍙敜灏忛": "ALT-NUMPAD3",
            "target鍙敜鎭愭儳鐚庣姮": "ALT-NUMPAD4",
            "鍙敜鎭堕瓟鍗＋": "ALT-NUMPAD5",
            "target鎭堕瓟涔嬬": "ALT-NUMPAD6",
            "target鏆楀奖绠?": "ALT-NUMPAD7",
            "鍐呯垎": "ALT-NUMPAD8",
            "target鍙敜鏈棩瀹堝崼": "ALT-NUMPAD9",
            "target鍙敜鎭堕瓟鏆村悰": "ALT-NUMPAD0",
        }

    def main_rotation(self, ctx: Context) -> tuple[str, float, str]:
        if not ctx.enable:
            return self.idle("总开关未开启")

        if ctx.delay:
            return self.idle("延迟开关开启")

        spell_queue_window = float(ctx.spell_queue_window or 0.3)
        player = ctx.player
        target = ctx.target
        latest_succeeded_cast = ctx.latest_succeeded_cast

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

        if not (target.exists and target.canAttack and target.isInRangedRange):
            return self.idle("没有合适的远程目标")

        soul_shards_cell = ctx.spec.cell(0)
        soul_shards_ratio = 0.0 if soul_shards_cell is None else soul_shards_cell.decimal
        soul_shards = round(soul_shards_ratio * 5)

        demon_core_stacks = player.buffStack("恶魔之核")
        dreadstalkers_ready = ctx.spell_cooldown_ready(
            "鍙敜鎭愭儳鐚庣姮", spell_queue_window
        )
        implosion_ready = ctx.spell_cooldown_ready("鍐呯垎", spell_queue_window)
        hand_ready = ctx.spell_cooldown_ready("鍙ゅ皵涓逛箣鎵?", spell_queue_window)
        demonbolt_ready = ctx.spell_cooldown_ready(
            "鎭堕瓟涔嬬", spell_queue_window
        )
        shadow_bolt_ready = ctx.spell_cooldown_ready(
            "鏆楀奖绠?", spell_queue_window
        )
        tyrant_ready = ctx.spell_cooldown_ready(
            "鍙敜鎭堕瓟鏆村悰", spell_queue_window
        )
        doomguard_ready = ctx.spell_cooldown_ready(
            "鍙敜鏈棩瀹堝崼", spell_queue_window
        )

        is_aoe = player.enemyCount >= 3
        portal_window = player.hasBuff("阿古斯传送门")
        tyrant_window = player.hasBuff("恶魔暴君")

        if doomguard_ready and (tyrant_ready or tyrant_window or portal_window):
            return self.cast("target鍙敜鏈棩瀹堝崼")

        if tyrant_ready and soul_shards >= 5:
            return self.cast("target鍙敜鎭堕瓟鏆村悰")

        if portal_window or tyrant_window:
            if hand_ready and soul_shards >= 3:
                return self.cast("target鍙ゅ皵涓逛箣鎵?")
            if demonbolt_ready and (demon_core_stacks >= 1 or soul_shards <= 3):
                return self.cast("target鎭堕瓟涔嬬")
            if dreadstalkers_ready and soul_shards >= 2:
                return self.cast("target鍙敜鎭愭儳鐚庣姮")

        if dreadstalkers_ready and soul_shards >= 2:
            return self.cast("target鍙敜鎭愭儳鐚庣姮")

        if is_aoe and implosion_ready and latest_succeeded_cast == "鍙ゅ皵涓逛箣鎵?":
            return self.cast("鍐呯垎")

        if hand_ready and soul_shards >= 4:
            return self.cast("target鍙ゅ皵涓逛箣鎵?")

        if demon_core_stacks >= 3 and demonbolt_ready:
            return self.cast("target鎭堕瓟涔嬬")

        if hand_ready and soul_shards >= 3 and not dreadstalkers_ready:
            return self.cast("target鍙ゅ皵涓逛箣鎵?")

        if demonbolt_ready and (demon_core_stacks >= 1 or soul_shards <= 3):
            return self.cast("target鎭堕瓟涔嬬")

        if shadow_bolt_ready:
            return self.cast("target鏆楀奖绠?")

        return self.idle("当前没有合适动作")
