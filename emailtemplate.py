# -*- coding: UTF-8 -*-

import os

from attr import attrs, attrib

default_template = """subject: __LAUNCH__, ТЗ на оснастки для кристаллов
message: Уважаемый(ая) __NAME__!

Напоминаю, что вам необходимо составить и выслать мне ТЗ на оснастки для следующих кристаллов:

__CHIP_LIST__

С уважением,
Копылов О.В.
"""


@attrs
class EmailTemplate(object):
    lines = attrib(init=False, type=list)
    file_name = attrib(default='email.tpl.txt', type=str)
    template = attrib(default=default_template, type=str)

    def __attrs_post_init__(self):
        path = f'./{self.file_name}'
        if os.path.isfile(path):
            with open(path, mode='rt', encoding='utf-8') as f:
                self.template = ''.join(f.readlines())
        else:
            self.save_template(self.template)
        self.lines = self.template.split('\n')

    def save_template(self, template):
        self.template = template
        self.lines = self.template.split('\n')
        with open(f'./{self.file_name}', mode='wt', encoding='utf-8') as f:
            f.write(template)

    @property
    def subject(self):
        return self.lines[0].strip('subject:')

    @property
    def message(self):
        return '\n'.join(self.lines[1:]).strip('message: ')



