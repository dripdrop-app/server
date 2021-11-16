import React, { useContext, useEffect, useMemo } from 'react';
import { TextField } from '@mui/material';
import { defaultTextFieldProps } from '../../utils/helpers';
import { MusicContext } from '../../context/Music';

const TagInputs = () => {
	const { updateFormInputs, formInputs } = useContext(MusicContext);
	const { title, artist, album, grouping } = formInputs;

	useEffect(() => {
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
		updateFormInputs({ album });
	}, [title, updateFormInputs]);

	return useMemo(
		() => (
			<React.Fragment>
				<TextField
					label="Title"
					required
					{...defaultTextFieldProps}
					value={title}
					onChange={(e) => updateFormInputs({ title: e.target.value })}
				/>
				<TextField
					label="Artist"
					required
					{...defaultTextFieldProps}
					value={artist}
					onChange={(e) => updateFormInputs({ artist: e.target.value })}
				/>
				<TextField
					label="Album"
					required
					{...defaultTextFieldProps}
					value={album}
					onChange={(e) => updateFormInputs({ album: e.target.value })}
				/>
				<TextField
					label="Grouping"
					{...defaultTextFieldProps}
					value={grouping}
					onChange={(e) => updateFormInputs({ grouping: e.target.value })}
				/>
			</React.Fragment>
		),
		[album, artist, grouping, title, updateFormInputs]
	);
};

export default TagInputs;
