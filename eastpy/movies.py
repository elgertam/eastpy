from __future__ import absolute_import, print_function, division

import abc
import sys

from typing import Callable, IO, cast

__author__ = 'Andrew Elgert, James Ladd'
__credits__ = ['Andrew Elgert', 'James Ladd']


class Movie(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def if_directed_by_do(self, director: str, action: Callable[['Movie'], None]) -> 'Movie':
        """Perform :action if movie directed by :director"""

    @abc.abstractmethod
    def if_title_do(self, title: str, action: Callable[['Movie'], None]) -> 'Movie':
        """Perform :action if movie title is :title"""

    @abc.abstractmethod
    def print_on_with_format(self, stream: IO[str]) -> 'Movie':
        """Print movie onto :stream using :format"""


class MovieFinder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def find_all_and_apply(self, action: Callable[[Movie], None]) -> 'MovieFinder':
        """Find all movies and apply :action"""


class MovieLister(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def apply_to_movies_directed_by(self, action: Callable[[Movie], None], director: str) -> 'MovieLister':
        """Execute :action on movies directed by by :director"""


class MoviesClient(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def append(self, movie: Movie) -> 'MoviesClient':
        """Append :movie onto stream using :formatter"""


class ExampleMovieLister(MovieLister):
    def __init__(self, finder: MovieFinder):
        self._finder = finder

    def apply_to_movies_directed_by(self, action: Callable[[Movie], None], director: str):
        self._finder.find_all_and_apply(lambda movie: movie.if_directed_by_do(director, action))
        return self


class ExampleMovie(Movie):
    def __init__(self, title: str, director: str):
        self._title = title
        self._director = director

    def if_directed_by_do(self, director: str, action: Callable[[Movie], None]):
        if self._director == director:
            action(self)
        return self

    def if_title_do(self, title: str, action: Callable[[Movie], None]):
        if self._title == title:
            action(self)
        return self

    def print_on_with_format(self, stream: IO[str]):
        stream.write('Movie (title: {}, director: {})\n'.format(self._title, self._director))
        return self


class ExampleMovieFinder(MovieFinder):
    _MOVIES = [
        ExampleMovie('Star Wars', director='George Lucas'),
        ExampleMovie('Lost Highway', director='David Lynch'),
        ExampleMovie('Naked Lunch', director='David Cronenberg'),
        ExampleMovie('Mulholland Dr', director='David Lynch'),
        ExampleMovie('The Adventures of Buckaroo Banzai Across the 8th Dimension', director='W.D. Richter'),
        ExampleMovie('Wild At Heart', director='David Lynch'),
    ]

    def find_all_and_apply(self, selector: Callable[[Movie], None]):
        for movie in self._MOVIES:
            selector(movie)


class ExampleMoviesClientStreamAdaptor(MoviesClient):
    def __init__(self, stream: IO[str]):
        self._stream = stream

    def append(self, movie: Movie):
        movie.print_on_with_format(self._stream)


class ExampleMoviesClientFileAdaptor(MoviesClient):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def append(self, movie: Movie):
        with cast(IO[str], open(self._file_path, 'a')) as f:
            movie.print_on_with_format(f)


if __name__ == '__main__':
    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        lambda movie: ExampleMoviesClientStreamAdaptor(sys.stdout).append(movie),
        'George Lucas'
    )

    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        lambda movie: ExampleMoviesClientStreamAdaptor(sys.stdout).append(movie),
        'David Lynch'
    )

    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        lambda movie: ExampleMoviesClientFileAdaptor("../movies.txt").append(movie),
        'David Cronenberg'
    )
