import React from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { CircularProgress, TextField } from '@mui/material';
import { defaultTextFieldProps } from '../../utils/helpers';
import { albumAtom, artistAtom, groupingLoadingAtom, groupingAtom, titleAtom } from '../../state/Music';

const TagInputs = () => {
	const [title, setTitle] = useAtom(titleAtom);
	const [artist, setArtist] = useAtom(artistAtom);
	const [album, setAlbum] = useAtom(albumAtom);
	const [grouping, setGrouping] = useAtom(groupingAtom);
	const groupingLoading = useAtomValue(groupingLoadingAtom);

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
			{groupingLoading ? (
				<CircularProgress />
			) : (
				<TextField
					label="Grouping"
					{...defaultTextFieldProps}
					value={grouping}
					onChange={(e) => setGrouping(e.target.value)}
				/>
			)}
		</React.Fragment>
	);
};

export default TagInputs;
