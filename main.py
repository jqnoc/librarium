from kivy.app import App
from kivy.uix.widget import Widget


class AshinamiWidget(Widget):
    pass


class AshinamiApp(App):
    def build(self):
        return AshinamiWidget()


if __name__ == '__main__':
    AshinamiApp().run()
