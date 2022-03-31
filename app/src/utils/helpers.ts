import { FetchBaseQueryError } from '@reduxjs/toolkit/dist/query';

export const resolveAlbumFromTitle = (title: string) => {
	let album = '';

	if (!title) {
		return album;
	}

	const openPar = title.indexOf('(');
	const closePar = title.indexOf(')');
	const specialTitle = (openPar !== -1 || closePar !== -1) && openPar < closePar;

	const songTitle = specialTitle ? title.substring(0, openPar).trim() : title.trim();
	album = songTitle;
	const songTitleWords = songTitle.split(' ');

	if (songTitleWords.length > 2) {
		album = songTitleWords.map((word) => word.charAt(0)).join('');
	}
	if (specialTitle) {
		const specialWords = title.substring(openPar + 1, closePar).split(' ');
		album = `${album} - ${specialWords[specialWords.length - 1]}`;
	} else {
		album = album ? `${album} - Single` : '';
	}
	return album;
};

export const isBase64 = (url: string) => RegExp(/^data:image/).test(url);

export const isValidImage = (url: string) => RegExp(/^http(s?):\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);

export const isValidLink = (url: string) => RegExp(/^http(s?):\/\/(www\.)?.*/).test(url);

export const isValidYTLink = (url: string) => RegExp(/^http(s?):\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(url);

export const isFetchBaseQueryError = (error: any): error is FetchBaseQueryError => 'status' in error;
