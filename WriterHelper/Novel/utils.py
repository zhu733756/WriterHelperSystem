# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
from haystack.utils import Highlighter
from django.utils.html import strip_tags
from datetime import datetime
import re

class BorkHighlighter(Highlighter):

    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        sentence_indexes= self.find_window(highlight_locations)
        if isinstance(sentence_indexes,tuple):
            start_offset,end_offset=sentence_indexes
            return self.render_html(highlight_locations, start_offset, end_offset)
        elif isinstance(sentence_indexes,list):
            highlighted_chunks=""
            for index in sentence_indexes:
                start_offset,end_offset=index
                highlighted_chunks+=self.render_html\
                    (highlight_locations,start_offset,end_offset)
            return highlighted_chunks

    def find_window(self, highlight_locations):

        # First, make sure we have words.
        if not len(highlight_locations):
            return 0, self.max_length

        words_found = []
        useful_sentences=[]

        # Next, make sure we found any words at all.
        for word, offset_list in highlight_locations.items():
            if len(offset_list):
                # Add all of the locations to the list.
                useful_sentences.extend(
                    [sentence for sentence in self.text_block.split("\n")
                            if sentence and word in sentence])

        sentence_indexes=[]
        for sentence in useful_sentences:
            sentence_indexes.extend(
                [m.span() for m in re.finditer(sentence, self.text_block)])

        if not len(sentence_indexes):
            return 0,self.max_length

        if len(sentence_indexes) == 1:
            return sentence_indexes[0]

        sentence_indexes=sorted(sentence_indexes,key=lambda x:x[0])
        return sentence_indexes

    def render_html(self, highlight_locations=None, start_offset=None, end_offset=None):
        # Start by chopping the block down to the proper window.

        text = self.text_block[start_offset:end_offset]

        if len(self.text_block) <= 15 and re.search("第.*章\s+.*", self.text_block):
            return text

        if (start_offset, end_offset) == (0, self.max_length):
            return text

        # Invert highlight_locations to a location -> term list
        term_list = []

        for term, locations in highlight_locations.items():
            term_list += [(loc - start_offset, term) for loc in locations]

        loc_to_term = sorted(term_list)

        hl_start='<span class="highlighted">'

        hl_end = '</span>'

        # Copy the part from the start of the string to the first match,
        # and there replace the match with a highlighted version.
        highlighted_chunk = ""
        matched_so_far = 0
        prev = 0
        prev_str = ""

        for cur, cur_str in loc_to_term:
            # This can be in a different case than cur_str
            actual_term = text[cur:cur + len(cur_str)]

            # Handle incorrect highlight_locations by first checking for the term
            if actual_term.lower() == cur_str:
                if cur < prev + len(prev_str):
                    continue

                highlighted_chunk += text[prev + len(prev_str):cur] + hl_start + actual_term + hl_end
                prev = cur
                prev_str = cur_str

                # Keep track of how far we've copied so far, for the last step
                matched_so_far = cur + len(actual_term)

        # Don't forget the chunk after the last term
        highlighted_chunk += text[matched_so_far:]

        timestamp=str(datetime.timestamp(datetime.now())).replace(".","")

        highlighted_chunks='<div><span id="timestamp%s">'%timestamp+highlighted_chunk+'</span>'\
                           '<button type="button" class="btn" data-clipboard-target="#timestamp%s">'\
                            '<span class="glyphicon glyphicon-hand-left"></span>' \
                            '</button></div>'%timestamp

        return highlighted_chunks













