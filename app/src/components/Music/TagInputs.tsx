import React, { useEffect } from 'react';
import { TextField } from '@mui/material';
import { defaultTextFieldProps, resolveAlbumFromTitle } from '../../utils/helpers';
import { albumSelector, artistSelector, groupingSelector, titleSelector } from '../../atoms/Music';
import { useRecoilState } from 'recoil';

const TagInputs = () => {
	const [title, setTitle] = useRecoilState(titleSelector);
	const [artist, setArtist] = useRecoilState(artistSelector);
	const [album, setAlbum] = useRecoilState(albumSelector);
	const [grouping, setGrouping] = useRecoilState(groupingSelector);

	useEffect(() => {
		setAlbum(resolveAlbumFromTitle(title));
	}, [setAlbum, title]);

	return (
		<React.Fragment>
			<TextField
				label="Title"
				required
				{...defaultTextFieldProps}
				value={title}
				onChange={(e) => setTitle(e.target.value)}
			/>
			<TextField
				label="Artist"
				required
				{...defaultTextFieldProps}
				value={artist}
				onChange={(e) => setArtist(e.target.value)}
			/>
			<TextField
				label="Album"
				required
				{...defaultTextFieldProps}
				value={album}
				onChange={(e) => setAlbum(e.target.value)}
			/>
			<TextField
				label="Grouping"
				{...defaultTextFieldProps}
				value={grouping}
				onChange={(e) => setGrouping(e.target.value)}
			/>
		</React.Fragment>
	);
};

export default TagInputs;
