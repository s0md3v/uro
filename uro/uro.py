import re
import sys
import argparse
from urllib.parse import urlparse


urlmap = {}
patterns_seen = []
content_patterns = []

blacklist = r'(post|blog)s?|docs|support/|/(\d{4}|pages?)/\d+/'
static_exts = ('js', 'css', 'png', 'pdf', 'jpg', 'jpeg', 'ico', 'bmp', 'svg', 'gif')


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


def is_seen(path: str) -> bool:
	"""
	checks if a url matches any recorded patterns
	"""
	for pattern in patterns_seen:
		if re.search(pattern, path):
			return compare_params(path)


def is_content(path: str) -> bool:
	"""
	checks if a path is likely to contain
	human written content e.g. a blog
	"""
	if path.count('-') > 3:
		new_parts = []
		for part in re.escape(path).split('/'):
			if part.count('-') > 3:
				new_parts.append('[^/]+')
			else:
				new_parts.append(part)
		content_patterns.append('/'.join(new_parts))
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


def is_blacklisted(path: str) -> bool:
	"""
	checks if the url matches the blacklist regex
	"""
	return re.search(blacklist, path)


def has_bad_ext(path: str) -> bool:
	"""
	checks if a url has a blacklisted extension
	"""
	return False if '/' in path.split('.')[-1] else path.lower().endswith(static_exts)

def main():
	if not sys.stdin.isatty():
		for line in sys.stdin:
			parsed = urlparse(line.strip())
			host = parsed.scheme + '://' + parsed.netloc
			path, params = parsed.path, params_to_dict(parsed.query)
			if host not in urlmap:
				urlmap[host] = {}
			if has_bad_ext(path):
				continue
			if not params:
				if is_content(path) or is_blacklisted(path):
					continue
				pattern = create_pattern(path)
				if matches_patterns(path):
					continue
				if '\\d+' in pattern and not pattern_exists(pattern):
					patterns_seen.append(pattern)
			if path not in urlmap[host]:
				urlmap[host][path] = [params] if params else []
			elif params and compare_params(urlmap[host][path], params):
				urlmap[host][path].append(params)
	for host, value in urlmap.items():
		for path, params in value.items():
			if params:
				for param in params:
					print(host + path + dict_to_params(param))
			elif '-' in path:
				matched = False
				for pattern in content_patterns:
					if re.search(pattern, path):
						matched = True
						break
				if not matched:
					print(host + path)
			else:
				print(host + path)
