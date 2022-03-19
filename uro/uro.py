import re
import sys
from urllib.parse import urlparse
try:
	from signal import signal, SIGPIPE, SIG_DFL
	signal(SIGPIPE, SIG_DFL)
except ImportError:
        pass

urlmap = {}
params_seen = []
patterns_seen = []

re_int = re.compile(r'/\d+([?/]|$)')
re_content = re.compile(r'(post|blog)s?|docs|support/|/(\d{4}|pages?)/\d+/')
static_exts = ('js', 'css', 'png', 'jpg', 'jpeg', 'svg',
	'ico','webp', 'ttf', 'otf', 'woff', 'gif',
	'pdf', 'bmp', 'eot', 'mp3', 'woff2', 'mp4', 'avi'
)


def params_to_dict(params: str) -> list:
	"""
	converts query string to dict
	"""
	the_dict = {}
	if params:
		for pair in params.split('&'):
			parts = pair.split('=')
			try:
				the_dict[parts[0]] = parts[1]
			except IndexError:
				pass
	return the_dict


def dict_to_params(params: dict) -> str:
	"""
	converts dict of params to query string
	"""
	stringed = [name + '=' + value for name, value in params.items()]
	return '?' + '&'.join(stringed)


def compare_params(og_params: list, new_params: dict) -> bool:
	"""
	checks if new_params contain a param
	that doesn't exist in og_params
	"""
	og_set = set([])
	for each in og_params:
		for key in each.keys():
			og_set.add(key)
	return set(new_params.keys()) - og_set


def is_content(path: str) -> bool:
	"""
	checks if a path is likely to contain
	human written content e.g. a blog
	"""
	for part in path.split('/'):
		if part.count('-') > 3:
			return True
	return False


def create_pattern(path: str) -> str:
	"""
	creates patterns for urls with integers in them
	"""
	new_parts = []
	for part in re.escape(path).split('/'):
		if part.isdigit():
			new_parts.append('\\d+')
		else:
			new_parts.append(part)
	return '/'.join(new_parts)


def pattern_exists(pattern: str) -> bool:
	"""
	checks if a int pattern exists
	"""
	for i, seen_pattern in enumerate(patterns_seen):
		if pattern in seen_pattern:
			patterns_seen[i] = pattern
			return True
		elif seen_pattern in pattern:
			return True
	return False


def matches_patterns(path: str) -> bool:
	"""
	checks if the url matches any of the int patterns
	"""
	for pattern in patterns_seen:
		if re.search(pattern, path):
			return True
	return False


def has_bad_ext(path: str) -> bool:
	"""
	checks if a url has a blacklisted extension
	"""
	return False if '/' in path.split('.')[-1] else path.lower().endswith(static_exts)


def is_new_param(params: list) -> bool:
	"""
	checks if a there's an unseen param within given params
	"""
	for param in params:
		if param in params_seen:
			return False
	return True


def main():
	if not sys.stdin.isatty():
		for line in sys.stdin:
			parsed = urlparse(line.strip())
			host = parsed.scheme + '://' + parsed.netloc
			if host not in urlmap:
				urlmap[host] = {}
			path, params = parsed.path, params_to_dict(parsed.query)
			has_new_param = False if not params else is_new_param(params.keys())
			new_params = [param for param in params.keys() if param not in params_seen]
			params_seen.extend(new_params)
			if has_bad_ext(path) or re_content.search(path) or is_content(path):
				continue
			if (not params or has_new_param) and re_int.match(path):
				pattern = create_pattern(path)
				if matches_patterns(path):
					continue
				if not pattern_exists(pattern):
					patterns_seen.append(pattern)
			elif path not in urlmap[host]:
				urlmap[host][path] = [params] if params else []
			elif has_new_param or compare_params(urlmap[host][path], params):
				urlmap[host][path].append(params)
	for host, value in urlmap.items():
		for path, params in value.items():
			if params:
				for param in params:
					print(host + path + dict_to_params(param))
			else:
				print(host + path)
