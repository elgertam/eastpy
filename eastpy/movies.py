from __future__ import absolute_import, print_function, division

import abc
import sys
import json

import attr
from attr import asdict

from typing import Callable, IO, cast

__author__ = 'Andrew Elgert, James Ladd'
__credits__ = ['Andrew Elgert', 'James Ladd']


@attr.s
class MovieValue(object):
    title = attr.ib(default='')
    director = attr.ib(default='')


class Movie(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def if_directed_by_do(self, director: str, action: Callable[['Movie'], None]) -> 'Movie':
        """Perform :action if movie directed by :director"""

    @abc.abstractmethod
    def if_title_do(self, title: str, action: Callable[['Movie'], None]) -> 'Movie':
        """Perform :action if movie title is :title"""

    def print_on_with_format(self, stream: IO[str], formatter: 'MovieFormatter') -> 'Movie':
        """
        Print movie onto :stream using :format

        Deprecated in favor of format_with(formatter).print_on(stream)
        """
        return self.format_with(formatter).print_on(stream)

    @abc.abstractmethod
    def format_with(self, formatter: 'MovieFormatter'):
        """Format movie with :formatter"""

    @abc.abstractmethod
    def print_on(self, stream: IO[str]):
        """Print movie onto :stream"""

    # TODO: Smell. Refactor to have "MoviePrinter" take care of formatting + printing using factories
    @abc.abstractmethod
    def set_format(self, formatted_movie: str) -> 'Movie':
        """Tell movie its formatted output"""


class MovieFormatter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def format_and_print_on(self, movie: MovieValue, stream: IO[str]) -> 'MovieFormatter':
        """
        Format :movie and print onto :stream

        Deprecated: don't use
        """

    @abc.abstractmethod
    def format(self, movie: Movie, title: str, director: str) -> 'MovieFormatter':
        """Format :movie and print onto :stream"""


class MovieFinder(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_all_and_apply(self, action: Callable[[Movie], None]) -> 'MovieFinder':
        """Find all movies and apply :action"""


class MovieLister(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def apply_to_movies_directed_by(self, action: Callable[[Movie], None], director: str) -> 'MovieLister':
        """Execute :action on movies directed by by :director"""


class MoviesClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, movie: Movie) -> 'MoviesClient':
        """Append :movie onto stream using :formatter"""


class SimpleStringMovieFormatter(MovieFormatter):
    # TODO: formatter should get data at create time without leaking it out; refactor to use __init__ and a factory
    def format(self, movie: Movie, title: str, director: str) -> 'MovieFormatter':
        movie.set_format(self._create_formatted_movie(title, director))
        return self

    def format_and_print_on(self, movie: MovieValue, stream: IO[str]):
        stream.write(self._create_formatted_movie(movie.title, movie.director))
        return self

    def _create_formatted_movie(self, title: str, director: str) -> str:
        return 'Movie (title: {}, director: {})\n'.format(title, director)


class JSONMovieFormatter(MovieFormatter):
    # TODO: formatter should get data at create time without leaking it out; refactor to use __init__ and a factory
    def format(self, movie: Movie, title: str, director: str) -> 'MovieFormatter':
        movie.set_format(self._create_formatted_movie(title, director))
        return self

    def format_and_print_on(self, movie: MovieValue, stream: IO[str]):
        stream.write(self._create_formatted_movie(**asdict(movie)))
        stream.write('\n')
        return self

    def _create_formatted_movie(self, title: str, director: str) -> str:
        return json.dumps({'title': title, 'director': director}) + '\n'


class JSONArrayMovieFormatter(MovieFormatter):
    # TODO: formatter should get data at create time without leaking it out; refactor to use __init__ and a factory
    def __init__(self):
        self._array = []
        self._stream = None

    def format(self, movie: Movie, title: str, director: str) -> 'MovieFormatter':
        self._array.append({'title': title, 'director': director})
        movie.set_format(self._create_formatted_movie())
        return self

    def format_and_print_on(self, movie: MovieValue, stream: IO[str]):
        if self._stream is None:
            self._stream = stream
        self._array.append(asdict(movie))

        stream.write(self._create_formatted_movie())
        return self

    def collect_and_print(self):
        if len(self._array) > 0 and self._stream is not None:
            self._stream.write(self._create_formatted_movie())

    def _create_formatted_movie(self) -> str:
        return json.dumps(self._array) + '\n'


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
        self._formatted_movie = ''

    def if_directed_by_do(self, director: str, action: Callable[[Movie], None]):
        if self._director == director:
            action(self)
        return self

    def if_title_do(self, title: str, action: Callable[[Movie], None]):
        if self._title == title:
            action(self)
        return self

    def set_format(self, formatted_movie: str) -> 'Movie':
        self._formatted_movie = formatted_movie
        return self

    def format_with(self, formatter: MovieFormatter):
        formatter.format(self, title=self._title, director=self._director)
        return self

    def print_on(self, stream: IO[str]):
        stream.write(self._formatted_movie)


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
    def __init__(self, stream: IO[str], formatter: MovieFormatter):
        self._stream = stream
        self._formatter = formatter

    def append(self, movie: Movie):
        movie.format_with(self._formatter).print_on(self._stream)


class ExampleMoviesClientFileAdaptor(MoviesClient):
    def __init__(self, file_path: str, formatter: MovieFormatter):
        self._file_path = file_path
        self._formatter = formatter

    def append(self, movie: Movie):
        with cast(IO[str], open(self._file_path, 'a')) as f:
            f.truncate()
            movie.format_with(self._formatter).print_on(f)


if __name__ == '__main__':
    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        lambda movie: ExampleMoviesClientStreamAdaptor(sys.stdout, JSONMovieFormatter()).append(movie),
        'George Lucas'
    )

    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        (lambda formatter: lambda movie: ExampleMoviesClientStreamAdaptor(sys.stdout, formatter).append(movie))(
            JSONArrayMovieFormatter()
        ),
        'David Lynch'
    )

    ExampleMovieLister(ExampleMovieFinder()).apply_to_movies_directed_by(
        lambda movie: ExampleMoviesClientFileAdaptor("../movies.txt", SimpleStringMovieFormatter()).append(movie),
        'David Lynch'
    )
