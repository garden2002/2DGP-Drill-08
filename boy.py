from pico2d import load_image, get_time

from state_machine import StateMachine, space_down, time_out, right_down, left_down, left_up, right_up, start_event,a_down


class Idle:
    @staticmethod
    def enter(boy , e):
        if right_down(e) or left_up(e):
            boy.action = 2
            boy.face_dir = -1
        elif left_down(e) or right_up(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1
        elif time_out(e):
            if boy.face_dir == -1:
                boy.action = 2
            else:
                boy.action = 3
        boy.frame = 0
        boy.dir = 0
        #시작 시간을 기록
        boy.start_time = get_time()
        pass
    @staticmethod
    def exit(boy , e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 5:
           #이벤트를 발생
           boy.state_machine.add_event(('TIME_OUT' , 0))
        pass
    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass

class Sleep:
    @staticmethod
    def enter(boy , e):
        if start_event(e):
            boy.face_dir = 1
            boy.action = 3
        boy.frame = 0
        pass
    @staticmethod
    def exit(boy , e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        pass
    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(
                boy.frame * 100,boy.action * 100 , 100 , 100 ,
                3.141592/2, # 회전각도
                ' ',  #좌우상하 반전 X
                boy.x - 25,boy.y - 25,100 ,100
            )
        else:
            boy.image.clip_composite_draw(
                boy.frame * 100, boy.action * 100, 100, 100,
                -3.141592 / 2,  # 회전각도
                ' ',  # 좌우상하 반전 X
                boy.x + 25, boy.y - 25, 100, 100
            )
        pass

class Run:
    @staticmethod
    def enter(boy , e):
        if right_down(e) or left_up(e):
            boy.action = 1
            boy.dir = 1
        elif left_down(e) or right_up(e):
            boy.action = 0
            boy.dir = -1
        boy.frame = 0

    @staticmethod
    def exit(boy , e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 3

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass

class AutoRun:
    @staticmethod
    def enter(boy , e):
        if boy.face_dir == 1:
            boy.action = 1
            boy.dir = 1
        else:
            boy.action = 0
            boy.dir = -1
        boy.frame = 0
        boy.start_time = get_time()
        pass

    @staticmethod
    def exit(boy , e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 10
        if get_time() - boy.start_time > 5:
           #이벤트를 발생
           boy.state_machine.add_event(('TIME_OUT' , 0))
        if boy.face_dir == 1 and boy.x >= 800:
            boy.face_dir = -1
            boy.action = 0
            boy.dir = -1
        elif boy.face_dir == -1 and boy.x <= 0:
            boy.face_dir = 1
            boy.action = 1
            boy.dir = 1

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 30 , 200 ,200)
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) #소년 객체를 위한 상태 머신인지 알려줄 필요
        self.state_machine.start(Idle) #객체를 생성한게 아닌, 직접 Idle 이라는 클래스를 사용
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, a_down: AutoRun,time_out: Sleep},
                Run: {right_down: Idle , left_down: Idle, right_up: Idle , left_up: Idle},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run , space_down: Idle},
                AutoRun: {right_down: Run , left_down: Run, right_up: Run , left_up: Run ,time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        #event : input event
        #state machine event : (이벤트종류, 값)
        self.state_machine.add_event(
            ('INPUT' , event)
        )
        pass

    def draw(self):
        self.state_machine.draw()
