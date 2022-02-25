import { TextFieldProps } from '@mui/material';
import { SxProps } from '@mui/system';

export const defaultTextFieldProps: TextFieldProps = {
	sx: { mx: 3, flex: 1 },
	variant: 'standard',
};

export const typographyDefaultCSS: SxProps = { textOverflow: 'ellipsis', whiteSpace: 'nowrap' };

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

export const isValidImage = (url: string) => RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);

export const isValidLink = (url: string) => RegExp(/^https:\/\/(www\.)?.*/).test(url);

export const isValidYTLink = (url: string) => RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(url);

interface ValidationError {
	loc: string[];
	msg: string;
	type: string;
}

export const apiValidatorErrorParser = (errors: ValidationError[]) => {
	return errors.reduce((msg, error) => {
		const field = error.loc.pop();
		console.log(field);
		if (field) {
			let message = error.msg.replace('value', field);
			message = message.charAt(0).toLocaleUpperCase() + message.substring(1);
			msg = !msg ? message : `${msg}, ${message}`;
		}
		return msg;
	}, '');
};
