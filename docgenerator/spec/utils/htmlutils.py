from spec.models import XMLElement, XMLAttribute, XMLRelationship
from spec.utils.relative_url import get_relative_url
import xml.sax

INDENT_SIZE = 3
DIFF_ELEMENT = 'metadiff'

class DiffElementContentHandler(xml.sax.handler.ContentHandler):
    def __init__(self, add_diffs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_diffs = add_diffs
        self.result = []
        self.pending_diff_class = None
        self.saw_diff = False

    def handle_start_diff_element(self):
        if self.add_diffs:
            self.pending_diff_class = 'diff'
            self.saw_diff = True

    def handle_end_diff_element(self):
        if self.add_diffs:
            self.pending_diff_class = 'nodiff'

    def get_pending_diff_markup(self):
        if self.pending_diff_class:
            result = f'</div><div class="xmlmarkup {self.pending_diff_class}">'
            self.pending_diff_class = None
        else:
            result = ''
        return result

    def get_result(self):
        html = '\n'.join(self.result)
        extraclass = ' nodiff' if self.saw_diff else ''
        return f'<div class="xmlmarkup{extraclass}">{html}</div>'

class XMLAugmenter(DiffElementContentHandler):
    def __init__(self, current_url, add_diffs, *args, **kwargs):
        super().__init__(add_diffs, *args, **kwargs)
        self.current_url = current_url
        self.element_stack = []
        self.last_tag_opened = None
        self.last_tag_opened_stack_size = 0

    def get_element_obj(self, name):
        qs = XMLElement.objects.filter(name=name)
        if self.element_stack:
            if self.element_stack[-1]:
                qs = qs.filter(child_rel__parent__id=self.element_stack[-1])
            else: # Previous element ID is None.
                qs = qs.none()
        try:
            obj = qs[0]
        except IndexError:
            obj = None
        return obj

    def get_attribute_markup(self, element_obj, attrs):
        result = []
        for k, v in attrs.items():
            start_tag = ''
            end_tag = ''
            if element_obj:
                attr_obj = None
                qs = XMLAttribute.objects.select_related('data_type')
                try:
                    attr_obj = qs.filter(
                        element=element_obj,
                        name=k
                    )[0]
                except IndexError:
                    try:
                        attr_obj = qs.filter(
                            attribute_group__xmlelement=element_obj
                        )[0]
                    except IndexError:
                        pass
                if attr_obj:
                    start_tag = f'<a href="{get_relative_url(self.current_url, attr_obj.data_type.get_absolute_url())}">'
                    end_tag = '</a>'
            result.append(f' <span class="attr">{k}="{start_tag}{v}{end_tag}"</span>')
        return ''.join(result)

    def startElement(self, name, attrs):
        if name == DIFF_ELEMENT:
            self.handle_start_diff_element()
            return
        obj = self.get_element_obj(name)
        if obj:
            start_tag = f'<a class="tag" href="{get_relative_url(self.current_url, obj.get_absolute_url())}">'
            end_tag = '</a>'
        else:
            start_tag = '<span class="tag">'
            end_tag = '</span>'
        if attrs:
            attr_string = self.get_attribute_markup(obj, attrs)
        else:
            attr_string = ''
        space = ' ' * len(self.element_stack) * INDENT_SIZE
        diff_html = self.get_pending_diff_markup()
        self.result.append(f'{diff_html}{space}&lt;{start_tag}{name}{end_tag}{attr_string}&gt;')
        self.last_tag_opened_stack_size = len(self.element_stack)
        self.element_stack.append(obj.id if obj else None)
        self.last_tag_opened = name

    def characters(self, content):
        if content and content.strip():
            space = ' ' * len(self.element_stack) * INDENT_SIZE
            self.result.append(f'{space}<span class="xmltxt">{content.strip()}</span>')

    def endElement(self, name):
        if name == DIFF_ELEMENT:
            self.handle_end_diff_element()
            return
        del self.element_stack[-1]
        if self.last_tag_opened == name and 'class="tag"' in self.result[-1] and len(self.element_stack) == self.last_tag_opened_stack_size:
            # As a nicety, make the element self-closing rather than
            # outputting a separate closing element.
            self.result[-1] = self.result[-1].replace('&gt;', '/&gt;')
        else:
            obj = self.get_element_obj(name)
            if obj:
                start_tag = f'<a class="tag" href="{get_relative_url(self.current_url, obj.get_absolute_url())}">'
                end_tag = '</a>'
            else:
                start_tag = '<span class="tag">'
                end_tag = '</span>'
            space = ' ' * len(self.element_stack) * INDENT_SIZE
            diff_html = self.get_pending_diff_markup()
            self.result.append(f'{diff_html}{space}&lt;/{start_tag}{name}{end_tag}&gt;')

def get_augmented_xml(current_url, xml_string, add_diffs=False):
    reader = xml.sax.make_parser()
    handler = XMLAugmenter(current_url, add_diffs)
    xml.sax.parseString(xml_string, handler)
    return (handler.saw_diff, handler.get_result())

class XMLPrettifier(DiffElementContentHandler):
    def __init__(self, add_diffs, *args, **kwargs):
        super().__init__(add_diffs, *args, **kwargs)
        self.indent_level = 0
        self.last_tag_opened = None

    def startElement(self, name, attrs):
        if name == DIFF_ELEMENT:
            self.handle_start_diff_element()
            return
        html = [
            self.get_pending_diff_markup(),
            ' ' * self.indent_level * INDENT_SIZE,
            f'&lt;{name}'
        ]
        if attrs:
            html.extend(f' {k}="{v}"' for (k, v) in attrs.items())
        html.append('&gt;')
        self.result.append(''.join(html))
        self.indent_level += 1
        self.last_tag_opened = name

    def characters(self, content):
        if content and content.strip():
            self.result.append((' ' * self.indent_level * INDENT_SIZE) + content.strip())

    def endElement(self, name):
        if name == DIFF_ELEMENT:
            self.handle_end_diff_element()
            return
        self.indent_level -= 1
        result = self.result
        if name == self.last_tag_opened:
            previous_line = result[-1].strip()
            if previous_line.startswith('&lt;'):
                result[-1] += f'&lt;/{name}&gt;'
            else:
                result[-2] += previous_line + f'&lt;/{name}&gt;'
                del result[-1]
        else:
            html = [
                self.get_pending_diff_markup(),
                ' ' * self.indent_level * INDENT_SIZE,
                f'&lt;/{name}&gt;'
            ]
            result.append(''.join(html))

def get_prettified_xml(xml_string):
    reader = xml.sax.make_parser()
    handler = XMLPrettifier(add_diffs=True)
    xml.sax.parseString(xml_string, handler)
    return handler.get_result()

def htmlescape(html:str):
    return html.replace('<', '&lt;').replace('>', '&gt;')

def get_element_subtree(current_url:str, el:XMLElement, els_seen:list):
    el_url = get_relative_url(current_url, el.get_absolute_url())
    result = [
        f'<a href="{el_url}">{htmlescape(el.name_with_brackets())}</a>'
    ]
    if el.id not in els_seen:
        els_seen.append(el.id)
        children = el.get_child_elements()
        if children:
            result.append('<ul class="nestedul">')
            for child in children:
                result.append('<li>')
                result.extend(get_element_subtree(current_url, child, els_seen))
                result.append('</li>')
            result.append('</ul>')
        els_seen.pop(-1)
    else:
        result.append('(recursive)')
    return result

def get_element_tree_html(current_url:str, root_el:XMLElement):
    result = ['<ul>']
    result.extend(get_element_subtree(current_url, root_el, []))
    result.append('</li></ul>')
    return '\n'.join(result)
