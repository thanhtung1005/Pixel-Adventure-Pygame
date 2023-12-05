"""
Some problems need to handle
    - Add event cling wall
    - Use "real time" to calculate position to remove lag when run in different devices
    - Add friction and acceleration
"""
import pygame

from Source.Utils import CharacterData
from Source.enums import (
    CharacterStatus,
    CharacterFacing,
    CharacterRelativePosition,
)


class Character(pygame.sprite.Sprite):

    def __init__(self, position: tuple, data: CharacterData) -> None:
        super().__init__()
        self.data = data
        # Player status
        self.status = CharacterStatus.Idle
        self.jumpOnAirCount = 0
        self.facing = CharacterFacing.Right
        self.relativePosition = CharacterRelativePosition.OnAir
        # Player image
        self.frameIndex = 0
        self.image = self.data.animations[self.status][self.frameIndex]
        #Player direction
        self.direction = pygame.math.Vector2(0, 0)
        # Player hitbox
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = pygame.Rect(position, (data.hitboxWidth, data.hitboxHeight))
        self.hitbox.midbottom = self.rect.midbottom
        return None

    def handleEvent(self) -> None:
        # Get event
        keys = pygame.key.get_pressed()
        # Move event
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = CharacterFacing.Right
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = CharacterFacing.Left
        else:
            self.direction.x = 0
        # Jump event
        if keys[pygame.K_w]:
            if self.relativePosition != CharacterRelativePosition.OnAir:
                self.direction.y = self.data.jumpSpeed
            else:
                if self.status == CharacterStatus.Fall and self.jumpOnAirCount < self.data.limitJumpOnAir:
                    self.status = CharacterStatus.JumpOnAir
                    self.direction.y = self.data.jumpOnAirSpeed[self.jumpOnAirCount]
                    self.jumpOnAirCount += 1
        return None

    def updateStatus(self) -> None:
        if self.direction.y < 0:
            if self.status != CharacterStatus.JumpOnAir:
                self.status = CharacterStatus.Jump
        elif self.direction.y > self.data.gravity:
            self.status = CharacterStatus.Fall
        else:
            if self.direction.x != 0:
                if self.relativePosition == CharacterRelativePosition.OnGround:
                    self.status = CharacterStatus.Run
                elif self.relativePosition == CharacterRelativePosition.OnWall:
                    self.status = CharacterStatus.ClingWall
            else:
                self.status = CharacterStatus.Idle
        return None

    def updateImage(self):
        animation = self.data.animations[self.status]
        self.frameIndex += self.data.animationSpeed
        if self.frameIndex >= len(animation):
            self.frameIndex = 0
        if self.facing == CharacterFacing.Right:
            self.image = animation[int(self.frameIndex)]
        elif self.facing == CharacterFacing.Left:
            self.image = pygame.transform.flip(
                surface=animation[int(self.frameIndex)], flip_x=True, flip_y=False
            )
        else:
            raise ValueError(f"Unkown character facing {self.facing}")
        return None

    def horizontalMove(self) -> None:
        self.rect.x += self.direction.x * self.data.runSpeed
        self.hitbox.x += self.direction.x * self.data.runSpeed
        return None

    def veticalMove(self) -> None:
        self.direction.y += self.data.gravity
        self.rect.y += self.direction.y
        self.hitbox.y += self.direction.y
        return None

    def update(self) -> None:
        self.handleEvent()
        self.updateStatus()
        self.updateImage()
        return None
