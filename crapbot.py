#!/usr/bin/env python2
import json
from random import choice, randint
from argparse import ArgumentParser
from urllib2 import urlopen

from praw import Reddit


class CrapBot:
    """ Bot to post crap """
    TERMINATORS = ('.', '?', '!')

    def __init__(self, args):
        """ Initialise """
        self.args = args
        self.tokens = self.read()
        self.token_count = len(self.tokens)
        self.cache = self.cache()

    def read(self):
        """ Get input tokens """
        with open(self.args.filename, 'r') as f:
            f.seek(0)
            return f.read().split()

    def cache(self):
        """ Get cache of triples """
        cache = {}
        for t1, t2, t3 in self.triples():
            key = (t1, t2)
            if key in cache:
                cache[key].append(t3)
            else:
                cache[key] = [t3]
        return cache

    def triples(self):
        """ Generator for token triples """
        if self.token_count < 3:
            return
        for i in xrange(self.token_count - 2):
            yield (self.tokens[i], self.tokens[i + 1], self.tokens[i + 2])

    def get_sentence(self, min_size=4, max_size=100):
        """ Generate a sentence """
        for i in xrange(max_size):
            self.t1, self.t2 = self.t2, choice(self.cache[(self.t1, self.t2)])
            yield self.t1 if i != 0 else self.t1.capitalize()
            if i > min_size and self.t1[-1] in self.TERMINATORS:
                raise StopIteration

    def get_text(self, size=3):
        """ Generate text of "size" number of sentences """
        seed = randint(0, self.token_count - 3)
        self.t1, self.t2 = self.tokens[seed], self.tokens[seed + 1]
        return ' '.join(' '.join(self.get_sentence()) for _ in xrange(size))

    def get_post(self):
        """ Get a post """
        r = Reddit(self.args.name)
        r.login(self.args.username, self.args.password)
        return r.get_subreddit(self.args.subreddit).get_new(limit=1).next()

    def run(self):
        """ Post some crap """
        text = self.get_text()
        post = self.get_post()
        post.add_comment(text)
        print '%s\n%s\n' % (post.short_link, text)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--subreddit', default='pics')
    parser.add_argument('--name', default='Trololol')
    parser.add_argument('--filename', default='input/heartofdarkness.txt')

    crapbot = CrapBot(parser.parse_args())
    crapbot.run()
