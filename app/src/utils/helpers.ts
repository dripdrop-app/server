import { TextFieldProps } from '@mui/material';
import { ContentTypes } from './enums';
import { SxProps } from '@mui/system';

export const defaultTextFieldProps: TextFieldProps = {
	sx: { mx: 3, flex: 1 },
	variant: 'standard',
};

export const typographyDefaultCSS: SxProps = { textOverflow: 'ellipsis', whiteSpace: 'nowrap' };

export const customFetch = async <SuccessResponse, FailedResponse>(
	input: RequestInfo,
	init?: RequestInit
): Promise<FetchResponse<SuccessResponse, FailedResponse>> => {
	const response = await fetch(input, init);
	const contentType = response.headers.get('Content-Type');
	let data = null;
	if (contentType) {
		if (contentType.includes(ContentTypes.TEXT)) {
			data = await response.text();
		} else if (contentType.includes(ContentTypes.JSON)) {
			data = await response.json();
		} else if (contentType.includes(ContentTypes.MP3_FILE)) {
			data = await response.blob();
		}
	}
	if (response.ok) {
		return { data, success: true, error: false };
	}
	const error = data ? (data.error ? data.error : data) : '';
	return { data: error, success: false, error: true };
};

export const resolveAlbumFromTitle = (title: string) => {
	let album = '';

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

export const isValidImage = (url: string) => RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);

export const isValidLink = (url: string) => RegExp(/^https:\/\/(www\.)?.*/).test(url);

export const isValidYTLink = (url: string) => RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(url);
